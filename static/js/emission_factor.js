// static/js/emission_factor.js

// ===== 页面初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

// ===== 数据状态 =====
let allData = [];
let selectedIds = new Set();
let editingId = null;

// ===== 完整的选项数据 =====
const optionsData = {
    // 因子类型 -> 类别
    "category_options": {
        "化石燃料排放因子": ["固体燃料", "液体燃料", "气体燃料"],
        "电网区域排放因子": ["全国电力", "区域电力"],
        "产品碳排放因子": ["运输服务", "装备产品", "办公用品"],
        "其他排放因子": ["热力供应"]
    },
    // 因子类型 -> 类别 -> 子类别
    "subcategory_options": {
        "化石燃料排放因子": {
            "固体燃料": ["无烟煤", "烟煤", "褐煤", "洗精煤", "煤制品", "焦炭"],
            "液体燃料": ["燃料油", "柴油", "汽油", "煤油"],
            "气体燃料": ["焦炉煤气", "城市煤气", "油田天然气", "气田天然气", "液化石油气", "液化天然气"]
        },
        "电网区域排放因子": {
            "全国电力": ["全国电力平均"],
            "区域电力": ["华北区域", "东北区域", "华东区域", "华中区域", "西北区域", "南方区域", "西南区域"]
        },
        "产品碳排放因子": {
            "运输服务": ["旅客运输", "货物运输", "废物循环"],
            "装备产品": ["铁路专用产品", "铁路通用产品"],
            "办公用品": ["电子设备", "车辆"]
        }
    },
    // 类别 -> 单位
    "unit_options": {
        "固体燃料": ["t"],
        "液体燃料": ["t"],
        "气体燃料": ["10^4Nm^3"],
        "全国电力": ["tCO2/MWh"],
        "区域电力": ["kgCO2/kWh"],
        "运输服务": ["kgCO2/人公里", "kgCO2/吨公里"],
        "装备产品": ["tCO2/件", "tCO2/公里", "tCO2/套", "tCO2/台"],
        "办公用品": ["tCO2/台", "tCO2/辆"],
        "热力供应": ["tCO2/GJ"]
    },
    // 因子类型对应的特定字段
    "special_fields": {
        "化石燃料排放因子": ["calorific_value", "carbon_content", "oxidation_rate"],
        "电网区域排放因子": ["region", "coverage"],
        "产品碳排放因子": ["product_type"]
    },
    // 区域选项
    "region_options": ["全国", "华北", "东北", "华东", "华中", "西北", "南方", "西南"],
    // 产品类型选项
    "product_type_options": ["道岔", "电缆", "受电弓", "空调", "照明灯具", "电脑", "公务车", "客运服务", "货运服务", "废物处理"],
    // 状态选项
    "status_options": ["启用", "历史"],
    // 数据来源选项
    "data_source_options": ["中国温室气体清单研究", "生态环境部", "中国产品全生命周期温室气体排放系数库", "推荐值", "历史数据", "企业自测", "行业标准", "国际数据库"]
};

// ===== 加载数据 =====
async function loadData() {
    showLoading(true);
    try {
        const response = await fetch('/api/emission_factors');
        if (!response.ok) {
            throw new Error('网络请求失败');
        }
        allData = await response.json();
        console.log('加载数据成功，共', allData.length, '条记录');

        renderTable(allData);
        loadTree();
        updateStatus(allData.length, selectedIds.size);
        updateTime();
    } catch (error) {
        console.error('加载数据失败:', error);
        showToast('加载数据失败: ' + error.message, 'error');
        const container = document.getElementById('treeContainer');
        if (container) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#95a5a6;">加载数据失败，请刷新重试</div>';
        }
    } finally {
        showLoading(false);
    }
}

// ===== 渲染表格 =====
function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align:center;padding:40px;color:#95a5a6;">暂无数据</td></tr>';
        return;
    }

    data.forEach((record) => {
        const tr = document.createElement('tr');
        tr.dataset.id = record.id;
        if (selectedIds.has(record.id)) {
            tr.classList.add('selected');
        }

        const checked = selectedIds.has(record.id) ? 'checked' : '';
        const factorValue = typeof record.factor_value === 'number' ? record.factor_value.toFixed(4) : record.factor_value || '';

        tr.innerHTML = `
            <td><input type="checkbox" class="row-checkbox" data-id="${record.id}" ${checked}></td>
            <td>${record.id}</td>
            <td>${record.factor_type || ''}</td>
            <td>${record.category || ''}</td>
            <td style="text-align:left;padding-left:12px;">${record.subcategory || ''}</td>
            <td>${record.unit || ''}</td>
            <td>${factorValue}</td>
            <td style="text-align:left;padding-left:12px;font-size:12px;">${record.data_source || ''}</td>
            <td>${record.effective_date || ''}</td>
            <td><span class="status-badge ${record.status === '启用' ? 'status-active' : 'status-history'}">${record.status || ''}</span></td>
            <td>
                <div class="action-btns">
                    <button class="btn-edit" onclick="editRecord(${record.id})" title="编辑">✏️</button>
                    <button class="btn-copy" onclick="copyRecord(${record.id})" title="复制">📋</button>
                    <button class="btn-delete" onclick="deleteRecord(${record.id})" title="删除">🗑️</button>
                </div>
            </td>
        `;

        tbody.appendChild(tr);
    });

    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.addEventListener('change', function() {
            const id = parseInt(this.dataset.id);
            if (this.checked) {
                selectedIds.add(id);
            } else {
                selectedIds.delete(id);
            }
            updateStatus(allData.length, selectedIds.size);
            updateRowStyle(id);
        });
    });
}

// ===== 树形结构 =====
function loadTree() {
    const container = document.getElementById('treeContainer');
    if (!container) return;

    if (!allData || allData.length === 0) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#95a5a6;">暂无数据</div>';
        return;
    }

    // 构建树结构：因子类型 -> 类别 -> 子类别
    const typeMap = new Map();
    allData.forEach(d => {
        if (d.factor_type) {
            if (!typeMap.has(d.factor_type)) {
                typeMap.set(d.factor_type, new Map());
            }
            const categoryMap = typeMap.get(d.factor_type);
            if (d.category) {
                if (!categoryMap.has(d.category)) {
                    categoryMap.set(d.category, new Set());
                }
                if (d.subcategory) {
                    categoryMap.get(d.category).add(d.subcategory);
                }
            }
        }
    });

    const typeOrder = ['化石燃料排放因子', '电网区域排放因子', '产品碳排放因子', '其他排放因子'];
    const sortedTypes = [...typeMap.keys()].sort((a, b) => {
        const idxA = typeOrder.indexOf(a);
        const idxB = typeOrder.indexOf(b);
        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
        if (idxA !== -1) return -1;
        if (idxB !== -1) return 1;
        return a.localeCompare(b);
    });

    let html = '';
    sortedTypes.forEach(type => {
        const categoryMap = typeMap.get(type);
        const typeCount = allData.filter(d => d.factor_type === type).length;

        html += `<div class="tree-node" data-type="type" data-value="${type}">
            <div class="tree-item" onclick="toggleTreeNode(this)">
                <span class="tree-toggle">▼</span>
                <span class="tree-label" onclick="selectTreeNode(this, 'type', '${escapeHtml(type)}')">${escapeHtml(type)}</span>
                <span class="tree-count">(${typeCount})</span>
            </div>
            <div class="tree-children">`;

        const sortedCategories = [...categoryMap.keys()].sort();
        sortedCategories.forEach(category => {
            const subcategories = [...categoryMap.get(category)];
            const categoryCount = allData.filter(d => d.factor_type === type && d.category === category).length;

            html += `<div class="tree-node" data-type="category" data-value="${category}">
                <div class="tree-item" onclick="toggleTreeNode(this)">
                    <span class="tree-toggle">▼</span>
                    <span class="tree-label" onclick="selectTreeNode(this, 'category', '${escapeHtml(type)}', '${escapeHtml(category)}')">${escapeHtml(category)}</span>
                    <span class="tree-count">(${categoryCount})</span>
                </div>
                <div class="tree-children">`;

            const sortedSubcategories = [...subcategories].sort();
            sortedSubcategories.forEach(subcategory => {
                const count = allData.filter(d => d.factor_type === type && d.category === category && d.subcategory === subcategory).length;
                html += `<div class="tree-node" data-type="subcategory" data-value="${subcategory}">
                    <div class="tree-item" onclick="toggleTreeNode(this)">
                        <span class="tree-toggle">&nbsp;</span>
                        <span class="tree-label" onclick="selectTreeNode(this, 'subcategory', '${escapeHtml(type)}', '${escapeHtml(category)}', '${escapeHtml(subcategory)}')">${escapeHtml(subcategory)}</span>
                        <span class="tree-count">(${count})</span>
                    </div>
                    <div class="tree-children"></div>
                </div>`;
            });

            html += `</div></div>`;
        });

        html += `</div></div>`;
    });

    container.innerHTML = html;
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function toggleTreeNode(element) {
    const node = element.closest('.tree-node');
    if (!node) return;

    const children = node.querySelector('.tree-children');
    const toggle = element.querySelector('.tree-toggle');

    if (children) {
        if (children.style.display === 'none') {
            children.style.display = 'block';
            if (toggle) toggle.textContent = '▼';
        } else {
            children.style.display = 'none';
            if (toggle) toggle.textContent = '▶';
        }
    }
}

function selectTreeNode(element, type, factorType, category, subcategory) {
    document.querySelectorAll('.tree-item.selected').forEach(el => el.classList.remove('selected'));
    const parentItem = element.closest('.tree-item');
    if (parentItem) {
        parentItem.classList.add('selected');
    }

    let filtered = allData;
    if (type === 'type') {
        filtered = allData.filter(d => d.factor_type === factorType);
    } else if (type === 'category') {
        filtered = allData.filter(d => d.factor_type === factorType && d.category === category);
    } else if (type === 'subcategory') {
        filtered = allData.filter(d => d.factor_type === factorType && d.category === category && d.subcategory === subcategory);
    }

    renderTable(filtered);
    updateStatus(filtered.length, selectedIds.size);
}

function expandAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.style.display = 'block';
        const toggle = el.closest('.tree-node')?.querySelector('.tree-toggle');
        if (toggle) toggle.textContent = '▼';
    });
}

function collapseAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.style.display = 'none';
        const toggle = el.closest('.tree-node')?.querySelector('.tree-toggle');
        if (toggle) toggle.textContent = '▶';
    });
}

// ===== 更新状态 =====
function updateStatus(total, selected) {
    const statusLabel = document.getElementById('statusLabel');
    if (statusLabel) {
        statusLabel.textContent = `共 ${total} 条记录 | 已选择 ${selected} 项`;
    }
}

function updateTime() {
    const now = new Date();
    const timeStr = now.getFullYear() + '-' +
        String(now.getMonth()+1).padStart(2,'0') + '-' +
        String(now.getDate()).padStart(2,'0') + ' ' +
        String(now.getHours()).padStart(2,'0') + ':' +
        String(now.getMinutes()).padStart(2,'0');
    const el = document.getElementById('updateLabel');
    if (el) el.textContent = '最后更新: ' + timeStr;
}

function updateRowStyle(id) {
    const tr = document.querySelector(`tr[data-id="${id}"]`);
    if (tr) {
        tr.classList.toggle('selected', selectedIds.has(id));
    }
}

// ===== 全选/取消全选 =====
function toggleAllCheckbox() {
    const mainCheckbox = document.getElementById('selectAllCheckbox');
    if (!mainCheckbox) return;

    const checked = mainCheckbox.checked;
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = checked;
        const id = parseInt(cb.dataset.id);
        if (checked) {
            selectedIds.add(id);
        } else {
            selectedIds.delete(id);
        }
        updateRowStyle(id);
    });
    updateStatus(allData.length, selectedIds.size);
}

function selectAll() {
    const cb = document.getElementById('selectAllCheckbox');
    if (cb) cb.checked = true;
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = true;
        const id = parseInt(cb.dataset.id);
        selectedIds.add(id);
        updateRowStyle(id);
    });
    updateStatus(allData.length, selectedIds.size);
}

function deselectAll() {
    const cb = document.getElementById('selectAllCheckbox');
    if (cb) cb.checked = false;
    document.querySelectorAll('.row-checkbox').forEach(cb => {
        cb.checked = false;
        const id = parseInt(cb.dataset.id);
        selectedIds.delete(id);
        updateRowStyle(id);
    });
    updateStatus(allData.length, selectedIds.size);
}

// ===== 表单联动 - 因子类型变化 =====
function onTypeChange() {
    const factorType = document.getElementById('factorType').value;
    const categorySelect = document.getElementById('category');
    const subcategorySelect = document.getElementById('subcategory');
    const unitSelect = document.getElementById('unit');
    const fuelFields = document.getElementById('fuelFields');
    const gridFields = document.getElementById('gridFields');
    const productFields = document.getElementById('productFields');

    // 清空下级选项
    categorySelect.innerHTML = '<option value="">请先选择因子类型</option>';
    subcategorySelect.innerHTML = '<option value="">请先选择类别</option>';
    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    // 隐藏所有特定字段
    fuelFields.style.display = 'none';
    gridFields.style.display = 'none';
    productFields.style.display = 'none';

    if (!factorType) return;

    // 更新类别选项
    const categories = optionsData.category_options[factorType] || [];
    categorySelect.innerHTML = '<option value="">请选择类别</option>';
    categories.forEach(c => {
        categorySelect.innerHTML += `<option value="${c}">${c}</option>`;
    });

    // 显示特定字段
    if (factorType === '化石燃料排放因子') {
        fuelFields.style.display = 'block';
    } else if (factorType === '电网区域排放因子') {
        gridFields.style.display = 'block';
    } else if (factorType === '产品碳排放因子') {
        productFields.style.display = 'block';
    }
}

// ===== 表单联动 - 类别变化 =====
function onCategoryChange() {
    const factorType = document.getElementById('factorType').value;
    const category = document.getElementById('category').value;
    const subcategorySelect = document.getElementById('subcategory');
    const unitSelect = document.getElementById('unit');

    subcategorySelect.innerHTML = '<option value="">请先选择类别</option>';
    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    if (!factorType || !category) return;

    // 更新子类别选项
    const subcategories = optionsData.subcategory_options[factorType]?.[category] || [];
    subcategorySelect.innerHTML = '<option value="">请选择子类别</option>';
    subcategories.forEach(s => {
        subcategorySelect.innerHTML += `<option value="${s}">${s}</option>`;
    });
}

// ===== 表单联动 - 子类别变化 =====
function onSubcategoryChange() {
    const category = document.getElementById('category').value;
    const unitSelect = document.getElementById('unit');

    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    if (!category) return;

    // 根据类别更新单位选项
    const units = optionsData.unit_options[category] || ['t', 'kg'];
    units.forEach(u => {
        unitSelect.innerHTML += `<option value="${u}">${u}</option>`;
    });
}

// ===== CRUD操作 =====
function addRecord() {
    editingId = null;
    document.getElementById('formTitle').textContent = '新增排放因子';
    document.getElementById('factorForm').reset();
    document.getElementById('editId').value = '';

    // 重置下拉框
    document.getElementById('factorType').value = '';
    document.getElementById('category').innerHTML = '<option value="">请先选择因子类型</option>';
    document.getElementById('subcategory').innerHTML = '<option value="">请先选择类别</option>';
    document.getElementById('unit').innerHTML = '<option value="">请选择单位</option>';
    document.getElementById('fuelFields').style.display = 'none';
    document.getElementById('gridFields').style.display = 'none';
    document.getElementById('productFields').style.display = 'none';
    document.getElementById('status').value = '启用';

    // 设置默认日期
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('effectiveDate').value = today;

    document.getElementById('formModal').style.display = 'flex';
}

function editRecord(id) {
    const record = allData.find(d => d.id === id);
    if (!record) {
        showToast('未找到该记录', 'error');
        return;
    }

    editingId = id;
    document.getElementById('formTitle').textContent = '编辑排放因子';
    document.getElementById('editId').value = id;

    // 设置值并触发联动
    document.getElementById('factorType').value = record.factor_type || '';
    onTypeChange();

    setTimeout(() => {
        document.getElementById('category').value = record.category || '';
        onCategoryChange();

        setTimeout(() => {
            document.getElementById('subcategory').value = record.subcategory || '';
            onSubcategoryChange();

            document.getElementById('unit').value = record.unit || '';
            document.getElementById('factorValue').value = record.factor_value || '';
            document.getElementById('dataSource').value = record.data_source || '';
            document.getElementById('effectiveDate').value = record.effective_date || '';
            document.getElementById('status').value = record.status || '启用';

            // 燃料字段
            if (record.calorific_value) {
                document.getElementById('calorificValue').value = record.calorific_value;
            }
            if (record.carbon_content) {
                document.getElementById('carbonContent').value = record.carbon_content;
            }
            if (record.oxidation_rate) {
                document.getElementById('oxidationRate').value = record.oxidation_rate;
            }

            // 电网字段
            if (record.region) {
                document.getElementById('region').value = record.region;
            }
            if (record.coverage) {
                document.getElementById('coverage').value = record.coverage;
            }

            // 产品字段
            if (record.product_type) {
                document.getElementById('productType').value = record.product_type;
            }
        }, 50);
    }, 50);

    document.getElementById('formModal').style.display = 'flex';
}

async function saveRecord() {
    const data = {
        factor_type: document.getElementById('factorType').value,
        category: document.getElementById('category').value,
        subcategory: document.getElementById('subcategory').value,
        unit: document.getElementById('unit').value,
        factor_value: parseFloat(document.getElementById('factorValue').value) || 0,
        data_source: document.getElementById('dataSource').value,
        effective_date: document.getElementById('effectiveDate').value,
        status: document.getElementById('status').value
    };

    // 验证必填字段
    const required = ['factor_type', 'category', 'subcategory', 'unit', 'factor_value'];
    const fieldNames = {
        'factor_type': '因子类型',
        'category': '类别',
        'subcategory': '子类别',
        'unit': '单位',
        'factor_value': '排放因子值'
    };

    for (const field of required) {
        if (!data[field]) {
            showToast(`${fieldNames[field] || field}不能为空`, 'warning');
            return;
        }
    }

    // 燃料字段
    if (data.factor_type === '化石燃料排放因子') {
        if (document.getElementById('calorificValue').value) {
            data.calorific_value = parseFloat(document.getElementById('calorificValue').value);
        }
        if (document.getElementById('carbonContent').value) {
            data.carbon_content = document.getElementById('carbonContent').value;
        }
        if (document.getElementById('oxidationRate').value) {
            data.oxidation_rate = document.getElementById('oxidationRate').value;
        }
    }

    // 电网字段
    if (data.factor_type === '电网区域排放因子') {
        if (document.getElementById('region').value) {
            data.region = document.getElementById('region').value;
        }
        if (document.getElementById('coverage').value) {
            data.coverage = document.getElementById('coverage').value;
        }
    }

    // 产品字段
    if (data.factor_type === '产品碳排放因子') {
        if (document.getElementById('productType').value) {
            data.product_type = document.getElementById('productType').value;
        }
    }

    const editId = document.getElementById('editId').value;
    const url = editId ? `/api/emission_factors/${editId}` : '/api/emission_factors';
    const method = editId ? 'PUT' : 'POST';

    showLoading(true);
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            closeModal();
            await loadData();
            showToast(editId ? '更新成功' : '添加成功', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || '操作失败', 'error');
        }
    } catch (error) {
        console.error('保存失败:', error);
        showToast('网络错误: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteRecord(id) {
    if (!confirm('确定要删除该排放因子吗？')) return;

    showLoading(true);
    try {
        const response = await fetch(`/api/emission_factors/${id}`, { method: 'DELETE' });
        if (response.ok) {
            selectedIds.delete(id);
            await loadData();
            showToast('删除成功', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || '删除失败', 'error');
        }
    } catch (error) {
        console.error('删除失败:', error);
        showToast('删除失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function copyRecord(id) {
    const original = allData.find(d => d.id === id);
    if (!original) {
        showToast('未找到该记录', 'error');
        return;
    }

    const newRecord = {
        ...original,
        subcategory: `复制 - ${original.subcategory}`
    };
    delete newRecord.id;

    showLoading(true);
    try {
        const response = await fetch('/api/emission_factors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newRecord)
        });

        if (response.ok) {
            await loadData();
            showToast('复制成功', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || '复制失败', 'error');
        }
    } catch (error) {
        console.error('复制失败:', error);
        showToast('复制失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function batchDelete() {
    if (selectedIds.size === 0) {
        showToast('请先选择要删除的记录', 'warning');
        return;
    }

    if (!confirm(`确定要删除选中的 ${selectedIds.size} 条记录吗？`)) return;

    showLoading(true);
    try {
        const response = await fetch('/api/emission_factors/batch_delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: Array.from(selectedIds) })
        });

        if (response.ok) {
            selectedIds.clear();
            await loadData();
            showToast('批量删除成功', 'success');
        } else {
            const error = await response.json();
            showToast(error.error || '批量删除失败', 'error');
        }
    } catch (error) {
        console.error('批量删除失败:', error);
        showToast('批量删除失败: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

async function exportData() {
    try {
        window.open('/api/emission_factors/export', '_blank');
        showToast('导出成功', 'success');
    } catch (error) {
        console.error('导出失败:', error);
        showToast('导出失败: ' + error.message, 'error');
    }
}

async function importData() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.xlsx,.xls,.csv';
    input.onchange = async function(e) {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        showLoading(true);
        try {
            const response = await fetch('/api/emission_factors/import', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                await loadData();
                showToast('导入成功', 'success');
            } else {
                const error = await response.json();
                showToast(error.error || '导入失败', 'error');
            }
        } catch (error) {
            console.error('导入失败:', error);
            showToast('导入失败: ' + error.message, 'error');
        } finally {
            showLoading(false);
        }
    };
    input.click();
}

// ===== 模态框 =====
function closeModal() {
    document.getElementById('formModal').style.display = 'none';
}

document.addEventListener('click', function(e) {
    const modal = document.getElementById('formModal');
    if (modal && modal.style.display === 'flex') {
        if (e.target.classList.contains('modal-overlay')) {
            closeModal();
        }
    }
});

// ===== Toast提示 =====
function showToast(message, type) {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        alert(message);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type || 'info'}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ===== 加载动画 =====
function showLoading(show) {
    let overlay = document.getElementById('loadingOverlay');
    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.className = 'loading-overlay';
            overlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(overlay);
        }
        overlay.style.display = 'flex';
    } else {
        if (overlay) {
            overlay.style.display = 'none';
        }
    }
}

// ===== 按Enter键提交表单 =====
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        const modal = document.getElementById('formModal');
        if (modal && modal.style.display === 'flex') {
            if (e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                saveRecord();
            }
        }
    }
});

// ===== 导出全局函数 =====
window.loadData = loadData;
window.loadTree = loadTree;
window.toggleTreeNode = toggleTreeNode;
window.selectTreeNode = selectTreeNode;
window.expandAll = expandAll;
window.collapseAll = collapseAll;
window.onTypeChange = onTypeChange;
window.onCategoryChange = onCategoryChange;
window.onSubcategoryChange = onSubcategoryChange;
window.toggleAllCheckbox = toggleAllCheckbox;
window.selectAll = selectAll;
window.deselectAll = deselectAll;
window.addRecord = addRecord;
window.editRecord = editRecord;
window.saveRecord = saveRecord;
window.deleteRecord = deleteRecord;
window.copyRecord = copyRecord;
window.batchDelete = batchDelete;
window.exportData = exportData;
window.importData = importData;
window.closeModal = closeModal;
window.showToast = showToast;
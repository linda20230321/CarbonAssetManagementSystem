// static/js/emission_source.js

// ===== 页面初始化 =====
document.addEventListener('DOMContentLoaded', function() {
    loadData();
});

// ===== 数据状态 =====
let allData = [];
let selectedIds = new Set();
let editingId = null;
let currentFilter = null;

// ===== 完整的选项数据 =====
const optionsData = {
    // 排放范围
    "range_options": ["直接排放（范围1）", "间接排放（范围2）", "其他间接排放（范围3）"],

    // 排放范围 -> 排放场景
    "scenario_options": {
        "直接排放（范围1）": ["牵引排放", "非牵引排放"],
        "间接排放（范围2）": ["牵引排放", "非牵引排放", "地点与市场基础电力", "自产可再生能源"],
        "其他间接排放（范围3）": ["采购的货物和服务", "资本货物", "燃料和能源相关活动", "上游运输和分销", "废物", "商务差旅", "员工通勤", "上游租赁资产"]
    },

    // 排放范围 -> 排放场景 -> 排放源类型
    "source_type_options": {
        "直接排放（范围1）": {
            "牵引排放": ["固体燃料", "液体燃料", "气体燃料"],
            "非牵引排放": ["固定源燃烧", "移动源燃烧", "装卸设备"]
        },
        "间接排放（范围2）": {
            "牵引排放": ["购电"],
            "非牵引排放": ["外购电力", "外购热力"],
            "地点与市场基础电力": ["电力"],
            "自产可再生能源": ["电力"]
        },
        "其他间接排放（范围3）": {
            "采购的货物和服务": ["铁路车辆", "装卸设备", "建筑物", "IT和电信"],
            "资本货物": ["铁路车辆", "装卸设备", "道路车辆和机械", "建筑物"],
            "燃料和能源相关活动": ["第三方"],
            "上游运输和分销": ["运输服务"],
            "废物": ["废物处理"],
            "商务差旅": ["商务差旅"],
            "员工通勤": ["员工通勤"],
            "上游租赁资产": ["租赁资产"]
        }
    },

    // 排放范围 -> 排放场景 -> 排放源类型 -> 排放源名称
    "source_name_options": {
        "直接排放（范围1）": {
            "牵引排放": {
                "固体燃料": ["无烟煤", "烟煤", "煤制品", "焦炭", "褐煤", "洗精煤"],
                "液体燃料": ["燃料油（重油）", "柴油", "汽油", "煤油"],
                "气体燃料": ["焦炉煤气、城市煤气", "油田天然气", "气田天然气", "液化石油气", "液化天然气"]
            },
            "非牵引排放": {
                "固定源燃烧": ["办公室、交通枢纽、终点站和仓库的供暖", "发电机", "任何其他固定燃烧"],
                "移动源燃烧": ["由机构营运的道路车辆及机械，包括租给雇员的车辆"],
                "装卸设备": ["由该机构操作的专业装卸设备"]
            }
        },
        "间接排放（范围2）": {
            "牵引排放": {
                "购电": ["电动列车(emu)和电动模式列车(BMUs)"]
            },
            "非牵引排放": {
                "外购电力": ["由该机构操作的道路车辆及机械", "由该机构操作的专业装卸设备", "由该机构营运的仓库、交汇处、终点站及办公室所消耗的电力"],
                "外购热力": ["由该组织运营的仓库、交汇处、终点站和办公室消耗的购买热量"]
            },
            "地点与市场基础电力": {
                "电力": ["地点与市场基础电力"]
            },
            "自产可再生能源": {
                "电力": ["自产可再生能源"]
            }
        },
        "其他间接排放（范围3）": {
            "采购的货物和服务": {
                "铁路车辆": ["铁路车辆维护承包商", "铁路车辆部件", "油品、润滑剂和添加剂（例如发动机油、液压油、防冻液）"],
                "装卸设备": ["设备部件", "油品、润滑剂和添加剂（例如发动机油、液压油、防冻液）"],
                "建筑物": ["清洁服务和用品，包括清洁人员旅行、使用洗涤剂、消毒剂和设备", "消耗品，如办公用品", "更换的固定装置和配件", "饮用水消耗"],
                "IT和电信": ["收据打印", "包括数据中心、云服务和软件的数字基础设施", "包括移动网络、无线电和内部通信系统的电信"]
            },
            "资本货物": {
                "铁路车辆": ["新的(租用的)机车车辆和马车", "铁路车辆部件(如未列入第一类排放源)"],
                "装卸设备": ["采购新的装卸设备，包括但不限于:吊运机、叉车、起重机和绞车、其他装卸设备"],
                "道路车辆和机械": ["购买新的道路车辆进行营运和维修", "购买新机器和设备，包括但不限于:运输和其他货运集装箱、火车清洗设备、其他用于铁路车辆维护的基本机械和工具"],
                "建筑物": ["报告机构建造的新建筑物及附属构筑物"]
            },
            "燃料和能源相关活动": {
                "第三方": ["燃油燃油税", "电力WTT", "电力的T&D"]
            },
            "上游运输和分销": {
                "运输服务": ["上游运输和分销"]
            },
            "废物": {
                "废物处理": ["废物处理"]
            },
            "商务差旅": {
                "商务差旅": ["商务旅行（汽车/公交车/火车/出租车）", "商务旅行（航空）", "酒店住宿（可选）"]
            },
            "员工通勤": {
                "员工通勤": ["员工通勤", "在家办公(可选)"]
            },
            "上游租赁资产": {
                "租赁资产": ["上游租赁资产"]
            }
        }
    },

    // 排放范围 -> 排放场景 -> 排放源类型 -> 活动类别
    "activity_options": {
        "直接排放（范围1）": {
            "非牵引排放": {
                "固定源燃烧": ["建筑物"],
                "移动源燃烧": ["道路车辆和机械"],
                "装卸设备": ["装卸设备"]
            }
        },
        "间接排放（范围2）": {
            "牵引排放": {
                "购电": ["铁路车辆"]
            },
            "非牵引排放": {
                "外购电力": ["道路车辆和机械", "装卸设备", "建筑物"],
                "外购热力": ["建筑物"]
            }
        },
        "其他间接排放（范围3）": {
            "采购的货物和服务": {
                "铁路车辆": ["铁路车辆"],
                "装卸设备": ["装卸设备"],
                "建筑物": ["建筑物"],
                "IT和电信": ["IT和电信"]
            },
            "资本货物": {
                "铁路车辆": ["铁路车辆"],
                "装卸设备": ["装卸设备"],
                "道路车辆和机械": ["道路车辆和机械"],
                "建筑物": ["建筑物"]
            },
            "燃料和能源相关活动": {
                "第三方": ["第三方"]
            },
            "商务差旅": {
                "商务差旅": ["商务差旅"]
            },
            "员工通勤": {
                "员工通勤": ["员工通勤"]
            }
        }
    },

    // 单位选项
    "unit_options": {
        "固体燃料": ["吨"],
        "液体燃料": ["吨"],
        "气体燃料": ["立方米"],
        "固定源燃烧": ["GJ", "kWh"],
        "移动源燃烧": ["升"],
        "装卸设备": ["kWh"],
        "购电": ["kWh"],
        "外购电力": ["kWh"],
        "外购热力": ["GJ"],
        "铁路车辆": ["次", "件", "升", "辆"],
        "建筑物": ["次", "件", "平方米"],
        "IT和电信": ["张", "月"],
        "道路车辆和机械": ["辆", "台"],
        "第三方": ["吨", "kWh"],
        "商务差旅": ["公里", "晚"],
        "员工通勤": ["公里", "天"]
    },

    // 数据来源选项
    "data_source_options": ["自动采集", "账单", "收据", "日志记录", "采购记录", "估算", "EC4T计费", "记录"]
};

// ===== 加载数据 =====
async function loadData() {
    showLoading(true);
    try {
        const response = await fetch('/api/emission_sources');
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

        tr.innerHTML = `
            <td><input type="checkbox" class="row-checkbox" data-id="${record.id}" ${checked}></td>
            <td>${record.id}</td>
            <td>${record.range_type || ''}</td>
            <td>${record.scenario_type || ''}</td>
            <td>${record.source_type || ''}</td>
            <td style="text-align:left;padding-left:12px;">${record.source_name || ''}</td>
            <td>${record.unit || ''}</td>
            <td>${record.activity_category || ''}</td>
            <td style="text-align:left;padding-left:12px;font-size:12px;">${record.equipment || ''}</td>
            <td>${record.data_source || ''}</td>
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
    if (!container) {
        console.warn('treeContainer 未找到');
        return;
    }

    console.log('开始构建树形结构，数据条数:', allData.length);

    if (!allData || allData.length === 0) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#95a5a6;">暂无数据</div>';
        return;
    }

    // 构建树结构：范围 -> 场景 -> 类型
    const rangeMap = new Map();
    allData.forEach(d => {
        if (d.range_type) {
            if (!rangeMap.has(d.range_type)) {
                rangeMap.set(d.range_type, new Map());
            }
            const scenarioMap = rangeMap.get(d.range_type);
            if (d.scenario_type) {
                if (!scenarioMap.has(d.scenario_type)) {
                    scenarioMap.set(d.scenario_type, new Set());
                }
                if (d.source_type) {
                    scenarioMap.get(d.scenario_type).add(d.source_type);
                }
            }
        }
    });

    // 定义范围的显示顺序
    const rangeOrder = ['直接排放（范围1）', '间接排放（范围2）', '其他间接排放（范围3）'];
    const sortedRanges = [...rangeMap.keys()].sort((a, b) => {
        const idxA = rangeOrder.indexOf(a);
        const idxB = rangeOrder.indexOf(b);
        if (idxA !== -1 && idxB !== -1) return idxA - idxB;
        if (idxA !== -1) return -1;
        if (idxB !== -1) return 1;
        return a.localeCompare(b);
    });

    let html = '';
    sortedRanges.forEach(range => {
        const scenarioMap = rangeMap.get(range);
        const rangeCount = allData.filter(d => d.range_type === range).length;

        // 场景排序
        const scenarioOrder = {
            '牵引排放': 1,
            '非牵引排放': 2,
            '采购的货物和服务': 3,
            '资本货物': 4,
            '燃料和能源相关活动': 5,
            '上游运输和分销': 6,
            '废物': 7,
            '商务差旅': 8,
            '员工通勤': 9,
            '上游租赁资产': 10,
            '地点与市场基础电力': 11,
            '自产可再生能源': 12
        };
        const sortedScenarios = [...scenarioMap.keys()].sort((a, b) => {
            const idxA = scenarioOrder[a] || 999;
            const idxB = scenarioOrder[b] || 999;
            if (idxA !== idxB) return idxA - idxB;
            return a.localeCompare(b);
        });

        html += `<div class="tree-node" data-type="range" data-value="${range}">
            <div class="tree-item" onclick="toggleTreeNode(this)">
                <span class="tree-toggle">▼</span>
                <span class="tree-label" onclick="selectTreeNode(this, 'range', '${escapeHtml(range)}')">${escapeHtml(range)}</span>
                <span class="tree-count">(${rangeCount})</span>
            </div>
            <div class="tree-children">`;

        sortedScenarios.forEach(scenario => {
            const sourceTypes = [...scenarioMap.get(scenario)];
            const scenarioCount = allData.filter(d => d.range_type === range && d.scenario_type === scenario).length;

            // 排放源类型排序
            const sourceTypeOrder = {
                '固体燃料': 1,
                '液体燃料': 2,
                '气体燃料': 3,
                '固定源燃烧': 4,
                '移动源燃烧': 5,
                '装卸设备': 6,
                '购电': 7,
                '外购电力': 8,
                '外购热力': 9,
                '电力': 10,
                '铁路车辆': 11,
                '建筑物': 12,
                'IT和电信': 13,
                '道路车辆和机械': 14,
                '第三方': 15,
                '商务差旅': 16,
                '员工通勤': 17
            };
            const sortedSourceTypes = [...sourceTypes].sort((a, b) => {
                const idxA = sourceTypeOrder[a] || 999;
                const idxB = sourceTypeOrder[b] || 999;
                if (idxA !== idxB) return idxA - idxB;
                return a.localeCompare(b);
            });

            html += `<div class="tree-node" data-type="scenario" data-value="${scenario}">
                <div class="tree-item" onclick="toggleTreeNode(this)">
                    <span class="tree-toggle">▼</span>
                    <span class="tree-label" onclick="selectTreeNode(this, 'scenario', '${escapeHtml(range)}', '${escapeHtml(scenario)}')">${escapeHtml(scenario)}</span>
                    <span class="tree-count">(${scenarioCount})</span>
                </div>
                <div class="tree-children">`;

            sortedSourceTypes.forEach(sourceType => {
                const count = allData.filter(d => d.range_type === range && d.scenario_type === scenario && d.source_type === sourceType).length;
                html += `<div class="tree-node" data-type="source_type" data-value="${sourceType}">
                    <div class="tree-item" onclick="toggleTreeNode(this)">
                        <span class="tree-toggle">&nbsp;</span>
                        <span class="tree-label" onclick="selectTreeNode(this, 'source_type', '${escapeHtml(range)}', '${escapeHtml(scenario)}', '${escapeHtml(sourceType)}')">${escapeHtml(sourceType)}</span>
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
    console.log('树形结构构建完成');
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

function selectTreeNode(element, type, range, scenario, sourceType) {
    document.querySelectorAll('.tree-item.selected').forEach(el => el.classList.remove('selected'));
    const parentItem = element.closest('.tree-item');
    if (parentItem) {
        parentItem.classList.add('selected');
    }

    let filtered = allData;
    if (type === 'range') {
        filtered = allData.filter(d => d.range_type === range);
    } else if (type === 'scenario') {
        filtered = allData.filter(d => d.range_type === range && d.scenario_type === scenario);
    } else if (type === 'source_type') {
        filtered = allData.filter(d => d.range_type === range && d.scenario_type === scenario && d.source_type === sourceType);
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

// ===== 表单联动 - 排放范围变化 =====
function onRangeChange() {
    const range = document.getElementById('rangeType').value;
    const scenarioSelect = document.getElementById('scenarioType');
    const sourceTypeSelect = document.getElementById('sourceType');
    const activitySelect = document.getElementById('activityCategory');
    const sourceNameInput = document.getElementById('sourceName');
    const sourceNameList = document.getElementById('sourceNameList');
    const unitSelect = document.getElementById('unit');

    // 清空下级选项
    scenarioSelect.innerHTML = '<option value="">请先选择排放范围</option>';
    sourceTypeSelect.innerHTML = '<option value="">请先选择排放场景</option>';
    activitySelect.innerHTML = '<option value="">请选择活动类别</option>';
    sourceNameInput.value = '';
    sourceNameList.innerHTML = '';
    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    if (!range) return;

    // 填充排放场景
    const scenarios = optionsData.scenario_options[range] || [];
    scenarioSelect.innerHTML = '<option value="">请选择排放场景</option>';
    scenarios.forEach(s => {
        scenarioSelect.innerHTML += `<option value="${s}">${s}</option>`;
    });
}

// ===== 表单联动 - 排放场景变化 =====
function onScenarioChange() {
    const range = document.getElementById('rangeType').value;
    const scenario = document.getElementById('scenarioType').value;
    const sourceTypeSelect = document.getElementById('sourceType');
    const activitySelect = document.getElementById('activityCategory');
    const sourceNameInput = document.getElementById('sourceName');
    const sourceNameList = document.getElementById('sourceNameList');
    const unitSelect = document.getElementById('unit');

    // 清空下级选项
    sourceTypeSelect.innerHTML = '<option value="">请先选择排放场景</option>';
    activitySelect.innerHTML = '<option value="">请选择活动类别</option>';
    sourceNameInput.value = '';
    sourceNameList.innerHTML = '';
    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    if (!range || !scenario) return;

    // 填充排放源类型
    const sourceTypes = optionsData.source_type_options[range]?.[scenario] || [];
    sourceTypeSelect.innerHTML = '<option value="">请选择排放源类型</option>';
    sourceTypes.forEach(s => {
        sourceTypeSelect.innerHTML += `<option value="${s}">${s}</option>`;
    });
}

// ===== 表单联动 - 排放源类型变化 =====
function onSourceTypeChange() {
    const range = document.getElementById('rangeType').value;
    const scenario = document.getElementById('scenarioType').value;
    const sourceType = document.getElementById('sourceType').value;
    const activitySelect = document.getElementById('activityCategory');
    const sourceNameInput = document.getElementById('sourceName');
    const sourceNameList = document.getElementById('sourceNameList');
    const unitSelect = document.getElementById('unit');

    // 清空下级选项
    activitySelect.innerHTML = '<option value="">请选择活动类别</option>';
    sourceNameInput.value = '';
    sourceNameList.innerHTML = '';
    unitSelect.innerHTML = '<option value="">请选择单位</option>';

    if (!range || !scenario || !sourceType) return;

    // 填充活动类别
    const activities = optionsData.activity_options[range]?.[scenario]?.[sourceType] || [];
    activitySelect.innerHTML = '<option value="">请选择活动类别</option>';
    activities.forEach(a => {
        activitySelect.innerHTML += `<option value="${a}">${a}</option>`;
    });

    // 填充排放源名称
    const sourceNames = optionsData.source_name_options[range]?.[scenario]?.[sourceType] || [];
    sourceNameList.innerHTML = '';
    sourceNames.forEach(s => {
        sourceNameList.innerHTML += `<option value="${s}">`;
    });

    // 根据排放源类型更新单位选项
    const units = optionsData.unit_options[sourceType] || ['吨'];
    unitSelect.innerHTML = '<option value="">请选择单位</option>';
    units.forEach(u => {
        unitSelect.innerHTML += `<option value="${u}">${u}</option>`;
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

// ===== 新增记录 =====
function addRecord() {
    editingId = null;
    document.getElementById('formTitle').textContent = '新增排放源';
    document.getElementById('sourceForm').reset();
    document.getElementById('editId').value = '';

    // 重置下拉框
    document.getElementById('rangeType').value = '';
    document.getElementById('scenarioType').innerHTML = '<option value="">请先选择排放范围</option>';
    document.getElementById('sourceType').innerHTML = '<option value="">请先选择排放场景</option>';
    document.getElementById('activityCategory').innerHTML = '<option value="">请选择活动类别</option>';
    document.getElementById('sourceNameList').innerHTML = '';
    document.getElementById('sourceName').value = '';
    document.getElementById('unit').innerHTML = '<option value="">请选择单位</option>';
    document.getElementById('equipment').value = '';
    document.getElementById('dataSource').value = '';

    document.getElementById('formModal').style.display = 'flex';
}

function editRecord(id) {
    const record = allData.find(d => d.id === id);
    if (!record) {
        showToast('未找到该记录', 'error');
        return;
    }

    editingId = id;
    document.getElementById('formTitle').textContent = '编辑排放源';
    document.getElementById('editId').value = id;

    // 设置值并触发联动
    document.getElementById('rangeType').value = record.range_type || '';
    onRangeChange();

    setTimeout(() => {
        document.getElementById('scenarioType').value = record.scenario_type || '';
        onScenarioChange();

        setTimeout(() => {
            document.getElementById('sourceType').value = record.source_type || '';
            onSourceTypeChange();

            document.getElementById('sourceName').value = record.source_name || '';
            document.getElementById('unit').value = record.unit || '';
            document.getElementById('activityCategory').value = record.activity_category || '';
            document.getElementById('equipment').value = record.equipment || '';
            document.getElementById('dataSource').value = record.data_source || '';
        }, 50);
    }, 50);

    document.getElementById('formModal').style.display = 'flex';
}

async function saveRecord() {
    const data = {
        range_type: document.getElementById('rangeType').value,
        scenario_type: document.getElementById('scenarioType').value,
        source_type: document.getElementById('sourceType').value,
        source_name: document.getElementById('sourceName').value.trim(),
        unit: document.getElementById('unit').value,
        activity_category: document.getElementById('activityCategory').value,
        equipment: document.getElementById('equipment').value.trim(),
        data_source: document.getElementById('dataSource').value,
        category_type: '货运物流类别'
    };

    // 验证必填字段
    const required = ['range_type', 'scenario_type', 'source_type', 'source_name', 'unit', 'data_source'];
    const fieldNames = {
        'range_type': '排放范围',
        'scenario_type': '排放场景',
        'source_type': '排放源类型',
        'source_name': '排放源名称',
        'unit': '单位',
        'data_source': '数据来源'
    };

    for (const field of required) {
        if (!data[field]) {
            showToast(`${fieldNames[field] || field}不能为空`, 'warning');
            return;
        }
    }

    const editId = document.getElementById('editId').value;
    const url = editId ? `/api/emission_sources/${editId}` : '/api/emission_sources';
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
    if (!confirm('确定要删除该排放源吗？')) return;

    showLoading(true);
    try {
        const response = await fetch(`/api/emission_sources/${id}`, { method: 'DELETE' });
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
        source_name: `复制 - ${original.source_name}`,
        category_type: '货运物流类别'
    };
    delete newRecord.id;

    showLoading(true);
    try {
        const response = await fetch('/api/emission_sources', {
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
        const response = await fetch('/api/emission_sources/batch_delete', {
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
        window.open('/api/emission_sources/export', '_blank');
        showToast('导出成功', 'success');
    } catch (error) {
        console.error('导出失败:', error);
        showToast('导出失败: ' + error.message, 'error');
    }
}

// ===== 关闭模态框 =====
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
window.onRangeChange = onRangeChange;
window.onScenarioChange = onScenarioChange;
window.onSourceTypeChange = onSourceTypeChange;
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
window.closeModal = closeModal;
window.showToast = showToast;
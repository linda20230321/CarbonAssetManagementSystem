// static/js/product_footprint.js
// ============================================================
// 产品碳足迹核算 - 完整前端逻辑
// ============================================================

var currentProductId = null;
var currentProductName = '';
var currentCategoryName = '';
var currentUnit = '';
var productConfigs = {};
var inputValues = {};
var allProducts = [];

// ============================================================
// 标签页切换
// ============================================================
function switchTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });
    document.querySelectorAll('.product-tab-content').forEach(function(el) {
        el.style.display = 'none';
    });
    var target = document.getElementById('tab-' + tab);
    if (target) {
        target.style.display = 'flex';
    }
    if (tab === 'overview') {
        renderProductTree('overviewTree', handleOverviewSelect);
    } else if (tab === 'calculator') {
        renderProductTree('productTree', handleProductSelect);
    } else if (tab === 'config') {
        renderProductTree('configTree', handleConfigSelect);
    } else if (tab === 'product') {
        loadProductList();
    }
}

// ============================================================
// 渲染产品树
// ============================================================
function renderProductTree(containerId, onSelect) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '<div style="padding:20px;text-align:center;color:#95a5a6;font-size:12px;">⏳ 加载中...</div>';

    fetch('/api/all_products')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (!Array.isArray(data)) {
            if (data && data.data && Array.isArray(data.data)) {
                data = data.data;
            } else if (data && typeof data === 'object') {
                data = [data];
            } else {
                data = [];
            }
        }

        allProducts = data;
        container.innerHTML = '';

        if (!data || data.length === 0) {
            container.innerHTML = '<div style="padding:20px;text-align:center;color:#e74c3c;font-size:12px;">❌ 暂无产品数据</div>';
            return;
        }

        var categories = {};
        data.forEach(function(p) {
            var cat = p.category_name || '未分类';
            if (!categories[cat]) {
                categories[cat] = { icon: p.icon || '📁', products: [] };
            }
            categories[cat].products.push(p);
        });

        var countEl = document.getElementById(containerId === 'overviewTree' ? 'overviewCount' : 'productCount');
        if (countEl) countEl.textContent = '共 ' + data.length + ' 种产品';

        var catKeys = Object.keys(categories);
        catKeys.forEach(function(cat) {
            var catData = categories[cat];
            var catDiv = document.createElement('div');
            catDiv.style.fontWeight = 'bold';
            catDiv.style.fontSize = '12px';
            catDiv.style.padding = '4px 8px';
            catDiv.style.color = '#2c3e50';
            catDiv.style.cursor = 'pointer';
            catDiv.style.background = '#f0f4f8';
            catDiv.style.marginBottom = '2px';
            catDiv.textContent = (catData.icon || '📁') + ' ' + cat;
            catDiv.onclick = function(e) {
                e.stopPropagation();
                var children = this.nextElementSibling;
                if (children) {
                    children.style.display = children.style.display === 'none' ? 'block' : 'none';
                }
            };
            container.appendChild(catDiv);

            var childContainer = document.createElement('div');
            childContainer.style.paddingLeft = '16px';
            childContainer.style.display = 'block';
            container.appendChild(childContainer);

            catData.products.forEach(function(p) {
                var prodDiv = document.createElement('div');
                prodDiv.className = 'product-tree-item';
                prodDiv.style.padding = '2px 8px';
                prodDiv.style.cursor = 'pointer';
                prodDiv.style.borderRadius = '3px';
                prodDiv.style.fontSize = '12px';
                prodDiv.textContent = '• ' + p.product_name;
                prodDiv.dataset.id = p.id;
                prodDiv.dataset.name = p.product_name;
                prodDiv.dataset.category = p.category_name;
                prodDiv.dataset.unit = p.unit || '件';
                prodDiv.onclick = function(e) {
                    document.querySelectorAll('#' + containerId + ' .product-tree-item').forEach(function(el) {
                        el.style.background = 'transparent';
                    });
                    this.style.background = '#e8f4fd';
                    if (onSelect) {
                        onSelect({
                            id: parseInt(this.dataset.id),
                            name: this.dataset.name,
                            category: this.dataset.category,
                            unit: this.dataset.unit
                        });
                    }
                };
                childContainer.appendChild(prodDiv);
            });
        });
    })
    .catch(function(e) {
        console.error('❌ 加载产品失败:', e);
        container.innerHTML = '<div style="padding:20px;text-align:center;color:#e74c3c;font-size:12px;">❌ 加载失败: ' + e.message + '</div>';
    });
}

// ============================================================
// 数据概览 - 周期变化
// ============================================================
function onOverviewPeriodChange() {
    var period = document.getElementById('overviewPeriod').value;
    var detail = document.getElementById('overviewPeriodDetail');
    detail.innerHTML = '';

    var currentYear = new Date().getFullYear();
    var years = [];
    for (var y = currentYear; y >= currentYear - 5; y--) {
        years.push(y);
    }
    var yearOptions = years.map(function(y) {
        return '<option value="' + y + '">' + y + '</option>';
    }).join('');

    if (period === '月度') {
        var months = [];
        for (var m = 1; m <= 12; m++) {
            months.push('<option value="' + m + '">' + m + '月</option>');
        }
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="overviewYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;" onchange="loadOverview()">
                    ${yearOptions}
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">月份</label>
                <select id="overviewMonth" class="form-control" style="width:55px; font-size:10px; padding:2px 4px;" onchange="loadOverview()">
                    ${months}
                </select>
            </div>
        `;
    } else if (period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="overviewYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;" onchange="loadOverview()">
                    ${yearOptions}
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">季度</label>
                <select id="overviewQuarter" class="form-control" style="width:55px; font-size:10px; padding:2px 4px;" onchange="loadOverview()">
                    <option value="Q1">Q1</option>
                    <option value="Q2">Q2</option>
                    <option value="Q3">Q3</option>
                    <option value="Q4">Q4</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="overviewYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;" onchange="loadOverview()">
                    ${yearOptions}
                </select>
            </div>
        `;
    }
    if (document.getElementById('overviewYear')) {
        document.getElementById('overviewYear').value = currentYear;
    }
}

// ============================================================
// 数据概览 - 加载数据
// ============================================================
function loadOverview() {
    if (!currentProductId) {
        return;
    }

    var area = document.getElementById('overviewArea');
    area.innerHTML = '<div style="text-align:center; color:#95a5a6; padding:40px 0; font-size:13px;">⏳ 加载数据中...</div>';

    var period = document.getElementById('overviewPeriod').value;
    var year = document.getElementById('overviewYear') ? document.getElementById('overviewYear').value : new Date().getFullYear();
    var month = document.getElementById('overviewMonth') ? document.getElementById('overviewMonth').value : null;
    var quarter = document.getElementById('overviewQuarter') ? document.getElementById('overviewQuarter').value : null;

    var params = new URLSearchParams({
        product_id: currentProductId,
        period: period,
        year: year
    });
    if (month) params.append('month', month);
    if (quarter) params.append('quarter', quarter);

    fetch('/api/product_overview?' + params.toString())
    .then(function(response) { return response.json(); })
    .then(function(data) {
        area.innerHTML = '';

        if (!data.has_data) {
            area.innerHTML = '<div class="overview-empty">📌 暂无碳足迹数据，请先在"碳足迹核算"页面进行计算</div>';
            return;
        }

        var total = data.total || 0;
        var stages = data.stages || {};
        var stageNames = {
            '原材料获取': '🌱 原材料获取',
            '生产制造': '🏭 生产制造',
            '运输交付': '🚚 运输交付',
            '使用阶段': '🔧 使用阶段',
            '维护保养': '🔩 维护保养',
            '报废回收': '♻️ 报废回收'
        };
        var colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c'];

        var periodInfo = '';
        if (period === '月度') {
            periodInfo = year + '年' + (month || '1') + '月';
        } else if (period === '季度') {
            periodInfo = year + '年' + (quarter || 'Q1');
        } else {
            periodInfo = year + '年';
        }

        var totalCard = document.createElement('div');
        totalCard.className = 'overview-total-card';
        totalCard.innerHTML = `
            <div>
                <div class="total-label">总碳排放量</div>
                <div class="total-number">${total.toFixed(2)}</div>
                <div style="font-size:12px; opacity:0.7;">kgCO₂e</div>
            </div>
            <div style="text-align:right; font-size:13px; opacity:0.8;">
                📅 ${periodInfo}<br>
                核算数量: ${data.quantity || 1} 件<br>
                核算时间: ${data.calculated_at || '-'}
            </div>
        `;
        area.appendChild(totalCard);

        var stageKeys = Object.keys(stages);
        if (stageKeys.length === 0) {
            var empty = document.createElement('div');
            empty.className = 'overview-empty';
            empty.textContent = '暂无阶段数据';
            area.appendChild(empty);
            return;
        }

        stageKeys.sort(function(a, b) {
            return (stages[b]?.value || 0) - (stages[a]?.value || 0);
        });

        var idx = 0;
        stageKeys.forEach(function(key) {
            var stageData = stages[key];
            if (!stageData) return;
            var pct = total > 0 ? (stageData.value / total * 100) : 0;
            var color = colors[idx % colors.length];

            var card = document.createElement('div');
            card.className = 'overview-stage-card';
            card.innerHTML = `
                <div class="stage-row">
                    <div>
                        <div class="stage-name">${stageNames[key] || key}</div>
                    </div>
                    <div style="display:flex; gap:16px; align-items:center; flex-wrap:wrap;">
                        <span class="stage-value" style="color:${color};">${stageData.value.toFixed(2)}</span>
                        <span class="stage-pct">${pct.toFixed(1)}% 贡献度</span>
                    </div>
                </div>
                <div class="stage-bar">
                    <div class="fill" style="width:${Math.max(pct, 1)}%; background:${color};"></div>
                </div>
            `;
            area.appendChild(card);
            idx++;
        });

        var note = document.createElement('div');
        note.style.cssText = 'margin-top:12px; padding:12px 16px; background:#f8f9fa; border-radius:4px; font-size:12px; color:#7f8c8d;';
        note.innerHTML = '📊 <strong>碳排放贡献度</strong>：各阶段碳排放占总排放量的百分比。';
        area.appendChild(note);
    })
    .catch(function(e) {
        console.error('❌ 加载概览数据失败:', e);
        area.innerHTML = '<div style="text-align:center; color:#e74c3c; padding:40px 0; font-size:13px;">❌ 加载失败: ' + e.message + '</div>';
    });
}

function refreshOverviewTree() {
    renderProductTree('overviewTree', handleOverviewSelect);
}

// ============================================================
// 数据概览 - 产品选择
// ============================================================
function handleOverviewSelect(product) {
    currentProductId = product.id;
    currentProductName = product.name;
    currentCategoryName = product.category;
    currentUnit = product.unit;

    document.getElementById('overviewProductName').textContent = product.name;
    document.getElementById('overviewProductInfo').textContent = (product.category || '') + ' | 单位: ' + (product.unit || '件');

    loadOverview();
}

// ============================================================
// 碳足迹核算 - 周期变化
// ============================================================
function onCalculatorPeriodChange() {
    var period = document.getElementById('calculatorPeriod').value;
    var detail = document.getElementById('calculatorPeriodDetail');
    detail.innerHTML = '';

    var currentYear = new Date().getFullYear();
    var years = [];
    for (var y = currentYear; y >= currentYear - 5; y--) {
        years.push(y);
    }
    var yearOptions = years.map(function(y) {
        return '<option value="' + y + '">' + y + '</option>';
    }).join('');

    if (period === '月度') {
        var months = [];
        for (var m = 1; m <= 12; m++) {
            months.push('<option value="' + m + '">' + m + '月</option>');
        }
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="calculatorYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;">
                    ${yearOptions}
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">月份</label>
                <select id="calculatorMonth" class="form-control" style="width:55px; font-size:10px; padding:2px 4px;">
                    ${months}
                </select>
            </div>
        `;
    } else if (period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="calculatorYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;">
                    ${yearOptions}
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">季度</label>
                <select id="calculatorQuarter" class="form-control" style="width:55px; font-size:10px; padding:2px 4px;">
                    <option value="Q1">Q1</option>
                    <option value="Q2">Q2</option>
                    <option value="Q3">Q3</option>
                    <option value="Q4">Q4</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">年份</label>
                <select id="calculatorYear" class="form-control" style="width:60px; font-size:10px; padding:2px 4px;">
                    ${yearOptions}
                </select>
            </div>
        `;
    } else if (period === '自定义') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">开始</label>
                <input type="date" id="calculatorStart" class="form-control" style="width:100px; font-size:10px; padding:2px 4px;" value="${currentYear}-01-01">
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:7px; color:#7f8c8d;">结束</label>
                <input type="date" id="calculatorEnd" class="form-control" style="width:100px; font-size:10px; padding:2px 4px;" value="${currentYear}-12-31">
            </div>
        `;
    }
    if (document.getElementById('calculatorYear')) {
        document.getElementById('calculatorYear').value = currentYear;
    }
}

// ============================================================
// 碳足迹核算 - 产品选择
// ============================================================
function handleProductSelect(product) {
    currentProductId = product.id;
    currentProductName = product.name;
    currentCategoryName = product.category;
    currentUnit = product.unit;

    document.getElementById('selectedProductName').textContent = product.name;
    document.getElementById('selectedProductInfo').textContent = (product.category || '') + ' | 单位: ' + (product.unit || '件');

    loadProductConfigs(product.id);
}

// ============================================================
// 加载产品配置
// ============================================================
function loadProductConfigs(productId) {
    var inputArea = document.getElementById('inputArea');
    inputArea.innerHTML = '<div style="text-align:center;color:#95a5a6;padding:20px;font-size:12px;">⏳ 加载配置中...</div>';

    fetch('/api/product_configs/' + productId)
    .then(function(response) { return response.json(); })
    .then(function(data) {
        productConfigs = data || {};
        renderInputFields();
    })
    .catch(function(e) {
        console.error('❌ 加载配置失败:', e);
        inputArea.innerHTML = '<div style="text-align:center;color:#e74c3c;padding:20px;font-size:12px;">❌ 加载失败: ' + e.message + '</div>';
    });
}

// ============================================================
// 渲染输入字段
// ============================================================
function renderInputFields() {
    var inputArea = document.getElementById('inputArea');
    var stages = ["原材料获取", "生产制造", "运输交付", "使用阶段", "维护保养", "报废回收"];
    inputValues = {};
    inputArea.innerHTML = '';

    var hasContent = false;

    stages.forEach(function(stage) {
        var checked = true;
        var cbs = document.querySelectorAll('.stage-checkbox');
        cbs.forEach(function(cb) {
            if (cb.value === stage && !cb.checked) {
                checked = false;
            }
        });
        if (!checked) return;

        var config = productConfigs[stage] || [];
        if (config.length === 0) return;
        hasContent = true;

        var stageDiv = document.createElement('div');
        stageDiv.style.border = '1px solid #e1e8ed';
        stageDiv.style.borderRadius = '4px';
        stageDiv.style.padding = '8px 12px';
        stageDiv.style.marginBottom = '6px';

        var title = document.createElement('div');
        title.textContent = '📌 ' + stage;
        title.style.fontWeight = 'bold';
        title.style.fontSize = '13px';
        title.style.color = '#2c3e50';
        title.style.marginBottom = '6px';
        stageDiv.appendChild(title);

        var categories = {};
        config.forEach(function(field) {
            var cat = field.category || '其他';
            if (!categories[cat]) categories[cat] = [];
            categories[cat].push(field);
        });

        var catKeys = Object.keys(categories);
        catKeys.forEach(function(cat) {
            var catLabel = document.createElement('div');
            catLabel.textContent = '【' + cat + '】';
            catLabel.style.fontSize = '11px';
            catLabel.style.color = '#7f8c8d';
            catLabel.style.marginTop = '4px';
            catLabel.style.marginBottom = '2px';
            stageDiv.appendChild(catLabel);

            var fieldsContainer = document.createElement('div');
            fieldsContainer.style.display = 'grid';
            fieldsContainer.style.gridTemplateColumns = '1fr 1fr';
            fieldsContainer.style.gap = '4px 20px';

            categories[cat].forEach(function(field) {
                var key = field.field_id || field.name;
                var row = document.createElement('div');
                row.style.display = 'flex';
                row.style.alignItems = 'center';
                row.style.gap = '4px';
                row.style.fontSize = '11px';
                row.style.padding = '2px 0';

                var label = document.createElement('span');
                var labelText = field.name + (field.unit ? ' (' + field.unit + ')' : '');
                label.textContent = labelText;
                label.style.minWidth = '100px';
                label.style.flex = '1';
                row.appendChild(label);

                var input;
                if (field.type === 'combobox') {
                    input = document.createElement('select');
                    (field.options || []).forEach(function(opt) {
                        var optEl = document.createElement('option');
                        optEl.value = opt;
                        optEl.textContent = opt;
                        if (opt === field.default) optEl.selected = true;
                        input.appendChild(optEl);
                    });
                    input.style.fontSize = '11px';
                    input.style.padding = '1px 4px';
                    input.style.border = '1px solid #d0d7de';
                    input.style.borderRadius = '3px';
                } else {
                    input = document.createElement('input');
                    input.type = 'number';
                    input.step = field.step || 1;
                    input.value = field.default || 0;
                    input.style.width = '80px';
                    input.style.fontSize = '11px';
                    input.style.padding = '1px 4px';
                    input.style.border = '1px solid #d0d7de';
                    input.style.borderRadius = '3px';
                    input.style.textAlign = 'right';
                }
                input.dataset.fieldId = key;
                input.dataset.factorKey = field.factor || field.factor_key || '';
                input.dataset.unit = field.unit || '';
                input.dataset.name = field.name;
                input.dataset.stage = stage;

                row.appendChild(input);

                var sourceLabel = document.createElement('span');
                var sourceText = (field.source || '次级数据') + ' | ' + (field.year || '') + ' | ' + (field.region || '');
                sourceLabel.textContent = sourceText;
                sourceLabel.style.fontSize = '8px';
                sourceLabel.style.color = field.source === '初级数据' ? '#2ecc71' : '#f39c12';
                sourceLabel.style.minWidth = '80px';
                row.appendChild(sourceLabel);

                fieldsContainer.appendChild(row);
                inputValues[key] = input;
            });

            stageDiv.appendChild(fieldsContainer);
        });

        inputArea.appendChild(stageDiv);
    });

    if (!hasContent) {
        inputArea.innerHTML = '<div style="text-align:center;color:#95a5a6;padding:20px;font-size:13px;">📌 当前产品暂无消耗源配置，请切换到"消耗源配置"页面进行配置</div>';
    }
}

// ============================================================
// 阶段选择变化
// ============================================================
function onStageChange() {
    if (currentProductId) {
        renderInputFields();
    }
}

// ============================================================
// 调整数量
// ============================================================
function adjustQty(delta) {
    var input = document.getElementById('calculateQty');
    var val = parseInt(input.value) || 1;
    input.value = Math.max(1, val + delta);
}

// ============================================================
// 碳足迹核算 - 计算
// ============================================================
function calculateFootprint() {
    if (!currentProductId) {
        alert('请先选择产品');
        return;
    }

    // 获取周期参数
    var period = document.getElementById('calculatorPeriod').value;
    var year = document.getElementById('calculatorYear') ? document.getElementById('calculatorYear').value : new Date().getFullYear();
    var month = document.getElementById('calculatorMonth') ? document.getElementById('calculatorMonth').value : null;
    var quarter = document.getElementById('calculatorQuarter') ? document.getElementById('calculatorQuarter').value : null;
    var start = document.getElementById('calculatorStart') ? document.getElementById('calculatorStart').value : null;
    var end = document.getElementById('calculatorEnd') ? document.getElementById('calculatorEnd').value : null;

    var quantity = parseInt(document.getElementById('calculateQty').value) || 1;
    var activities = [];

    var inputs = document.querySelectorAll('#inputArea input[type="number"]');
    inputs.forEach(function(input) {
        var val = parseFloat(input.value) || 0;
        if (val > 0 && input.dataset.factorKey) {
            activities.push({
                stage: input.dataset.stage || '',
                name: input.dataset.name || '',
                quantity: val,
                unit: input.dataset.unit || '',
                factor_key: input.dataset.factorKey || ''
            });
        }
    });

    if (activities.length === 0) {
        alert('请至少输入一个有效数据');
        return;
    }

    var btn = document.querySelector('#tab-calculator .btn-success');
    if (!btn) {
        btn = document.querySelector('.btn-success');
    }
    var originalText = btn.textContent;
    btn.textContent = '⏳ 计算中...';
    btn.disabled = true;

    var data = {
        product_id: currentProductId,
        product_name: currentProductName,
        category_name: currentCategoryName,
        quantity: quantity,
        period: period,
        year: parseInt(year),
        month: month ? parseInt(month) : null,
        quarter: quarter || null,
        period_start: start || null,
        period_end: end || null,
        activities: activities
    };

    fetch('/api/calculate_footprint', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(function(response) { return response.json(); })
    .then(function(result) {
        btn.textContent = originalText;
        btn.disabled = false;
        if (result.error) {
            alert('计算失败: ' + result.error);
            return;
        }
        showResult(result, quantity);
    })
    .catch(function(e) {
        btn.textContent = originalText;
        btn.disabled = false;
        alert('计算失败: ' + e.message);
    });
}

// ============================================================
// 显示结果
// ============================================================
function showResult(result, quantity) {
    var modal = document.getElementById('resultModal');
    var content = document.getElementById('resultContent');
    var title = document.getElementById('resultTitle');
    title.textContent = currentProductName + ' 碳足迹核算结果';

    var html = '';
    html += '<div class="result-total">';
    html += '<span class="number">' + result.total.toFixed(2) + '</span>';
    html += '<span class="unit">kgCO₂e</span>';
    html += '<span class="qty">(核算数量: ' + quantity + ' 件)</span>';
    html += '</div>';

    html += '<div class="result-stages">';
    var colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6', '#1abc9c'];
    var idx = 0;
    for (var stage in result.stages) {
        var data = result.stages[stage];
        html += '<div class="result-stage-card" style="border-left-color:' + colors[idx % colors.length] + ';">';
        html += '<div class="stage-name">' + stage + '</div>';
        html += '<div class="stage-value" style="color:' + colors[idx % colors.length] + ';">' + data.value.toFixed(0) + '</div>';
        html += '<div class="stage-pct">' + data.percentage.toFixed(1) + '%</div>';
        html += '</div>';
        idx++;
    }
    html += '</div>';

    html += '<div class="result-table-wrap">';
    html += '<table>';
    html += '<thead><tr>';
    html += '<th>阶段</th><th>消耗源</th><th>消耗量</th><th>排放量(kgCO₂e)</th><th>占比(%)</th>';
    html += '</tr></thead><tbody>';

    var details = result.details || [];
    details.forEach(function(item) {
        var pct = result.total > 0 ? (item.emission / result.total * 100) : 0;
        html += '<tr>';
        html += '<td>' + item.stage + '</td>';
        html += '<td>' + item.name + '</td>';
        html += '<td>' + item.quantity.toFixed(1) + ' ' + item.unit + '</td>';
        html += '<td><strong>' + item.emission.toFixed(2) + '</strong></td>';
        html += '<td>' + pct.toFixed(1) + '%</td>';
        html += '</tr>';
    });
    html += '</tbody></table></div>';

    content.innerHTML = html;
    modal.style.display = 'flex';
}

function closeResultModal() {
    document.getElementById('resultModal').style.display = 'none';
}

// ============================================================
// 消耗源配置 - 产品选择
// ============================================================
var selectedConfigProductId = null;

function handleConfigSelect(product) {
    selectedConfigProductId = product.id;
    currentProductName = product.name;
    document.getElementById('configProductName').textContent = product.name + ' (' + (product.category || '') + ')';
    loadConfigForEdit(product.id);
}

function loadConfigForEdit(productId) {
    var area = document.getElementById('configArea');
    area.innerHTML = '<div style="text-align:center;color:#95a5a6;padding:20px;font-size:12px;">⏳ 加载配置中...</div>';

    fetch('/api/product_configs/' + productId)
    .then(function(response) { return response.json(); })
    .then(function(data) {
        productConfigs = data || {};
        renderConfigEditor();
    })
    .catch(function(e) {
        area.innerHTML = '<div style="text-align:center;color:#e74c3c;padding:20px;font-size:12px;">❌ 加载失败: ' + e.message + '</div>';
    });
}

function renderConfigEditor() {
    var area = document.getElementById('configArea');
    var stages = ["原材料获取", "生产制造", "运输交付", "使用阶段", "维护保养", "报废回收"];
    area.innerHTML = '';

    stages.forEach(function(stage) {
        var config = productConfigs[stage] || [];
        var stageDiv = document.createElement('div');
        stageDiv.className = 'config-stage-card';

        var title = document.createElement('div');
        title.className = 'stage-title';

        var titleLabel = document.createElement('span');
        titleLabel.textContent = '📌 ' + stage;
        title.appendChild(titleLabel);

        var btnGroup = document.createElement('div');
        btnGroup.style.display = 'flex';
        btnGroup.style.gap = '4px';

        var addBtn = document.createElement('button');
        addBtn.textContent = '+ 添加';
        addBtn.className = 'btn btn-sm btn-primary';
        addBtn.style.fontSize = '9px';
        addBtn.style.padding = '2px 8px';
        addBtn.onclick = function() { openFieldModal(stage); };
        btnGroup.appendChild(addBtn);

        title.appendChild(btnGroup);
        stageDiv.appendChild(title);

        if (config.length === 0) {
            var empty = document.createElement('div');
            empty.className = 'empty-hint';
            empty.textContent = '该阶段暂无配置，点击"添加"创建消耗源';
            stageDiv.appendChild(empty);
        } else {
            var table = document.createElement('table');
            table.className = 'config-table';

            var thead = document.createElement('thead');
            thead.innerHTML = '<tr>' +
                '<th>字段名称</th><th>类型</th><th>单位</th>' +
                '<th>默认值</th><th>排放因子</th><th>分类</th><th>操作</th>' +
                '</tr>';
            table.appendChild(thead);

            var tbody = document.createElement('tbody');
            config.forEach(function(field, index) {
                var tr = document.createElement('tr');
                tr.innerHTML = '<td><strong>' + (field.name || '') + '</strong></td>' +
                    '<td>' + (field.type || 'number') + '</td>' +
                    '<td>' + (field.unit || '') + '</td>' +
                    '<td>' + (field.default || '') + '</td>' +
                    '<td style="font-size:9px;color:#2980b9;">' + (field.factor || field.factor_key || '-') + '</td>' +
                    '<td style="font-size:9px;">' + (field.category || '') + '</td>';

                var actionTd = document.createElement('td');

                var editBtn = document.createElement('button');
                editBtn.textContent = '编辑';
                editBtn.className = 'field-action-btn btn-edit';
                editBtn.onclick = function() { openFieldModal(stage, field, index); };
                actionTd.appendChild(editBtn);

                var delBtn = document.createElement('button');
                delBtn.textContent = '删除';
                delBtn.className = 'field-action-btn btn-delete';
                delBtn.onclick = function() { deleteConfigField(stage, index); };
                actionTd.appendChild(delBtn);

                tr.appendChild(actionTd);
                tbody.appendChild(tr);
            });
            table.appendChild(tbody);
            stageDiv.appendChild(table);
        }

        area.appendChild(stageDiv);
    });
}

// ============================================================
// 字段编辑弹窗
// ============================================================
function openFieldModal(stage, field, index) {
    var modal = document.getElementById('fieldModal');
    var title = document.getElementById('fieldModalTitle');
    var editStage = document.getElementById('editStage');
    var editFieldId = document.getElementById('editFieldId');

    if (field) {
        title.textContent = '编辑消耗源字段';
        editStage.value = stage;
        editFieldId.value = index !== undefined ? index : '';
        document.getElementById('fieldName').value = field.name || '';
        document.getElementById('fieldType').value = field.type || 'number';
        document.getElementById('fieldUnit').value = field.unit || '';
        document.getElementById('fieldDefault').value = field.default || '';
        document.getElementById('fieldFactor').value = field.factor || field.factor_key || '';
        document.getElementById('fieldOptions').value = (field.options || []).join(',');
        document.getElementById('fieldCategory').value = field.category || '其他';
        document.getElementById('fieldStep').value = field.step || 100;
        document.getElementById('fieldSource').value = field.source || '次级数据';
        document.getElementById('fieldYear').value = field.year || 2024;
        document.getElementById('fieldRegion').value = field.region || '全国';
    } else {
        title.textContent = '添加消耗源字段 - ' + stage;
        editStage.value = stage;
        editFieldId.value = '';
        document.getElementById('fieldName').value = '';
        document.getElementById('fieldType').value = 'number';
        document.getElementById('fieldUnit').value = '';
        document.getElementById('fieldDefault').value = '';
        document.getElementById('fieldFactor').value = '';
        document.getElementById('fieldOptions').value = '';
        document.getElementById('fieldCategory').value = '其他';
        document.getElementById('fieldStep').value = '100';
        document.getElementById('fieldSource').value = '次级数据';
        document.getElementById('fieldYear').value = '2024';
        document.getElementById('fieldRegion').value = '全国';
    }

    toggleOptionsGroup();
    modal.style.display = 'flex';
}

function closeFieldModal() {
    document.getElementById('fieldModal').style.display = 'none';
}

function toggleOptionsGroup() {
    var type = document.getElementById('fieldType').value;
    var group = document.getElementById('optionsGroup');
    group.style.display = type === 'combobox' ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', function() {
    var fieldType = document.getElementById('fieldType');
    if (fieldType) {
        fieldType.addEventListener('change', toggleOptionsGroup);
    }
});

function saveField() {
    var stage = document.getElementById('editStage').value;
    var fieldId = document.getElementById('editFieldId').value;
    var name = document.getElementById('fieldName').value.trim();
    var type = document.getElementById('fieldType').value;
    var unit = document.getElementById('fieldUnit').value.trim();
    var defaultValue = document.getElementById('fieldDefault').value.trim();
    var factor = document.getElementById('fieldFactor').value.trim();
    var options = document.getElementById('fieldOptions').value.trim();
    var category = document.getElementById('fieldCategory').value;
    var step = parseFloat(document.getElementById('fieldStep').value) || 100;
    var source = document.getElementById('fieldSource').value;
    var year = parseInt(document.getElementById('fieldYear').value) || 2024;
    var region = document.getElementById('fieldRegion').value.trim() || '全国';

    if (!name) {
        alert('请输入字段名称');
        return;
    }
    if (!unit && type !== 'combobox') {
        alert('请输入单位');
        return;
    }

    var fieldData = {
        field_id: 'field_' + Date.now(),
        name: name,
        type: type,
        unit: unit,
        default: defaultValue || '0',
        source: source,
        year: year,
        region: region,
        step: step,
        category: category
    };

    if (factor) {
        fieldData.factor = factor;
    }
    if (type === 'combobox' && options) {
        fieldData.options = options.split(',').map(function(o) { return o.trim(); });
    }

    if (fieldId !== '' && fieldId !== 'undefined') {
        var idx = parseInt(fieldId);
        if (productConfigs[stage] && productConfigs[stage][idx]) {
            fieldData.field_id = productConfigs[stage][idx].field_id || fieldData.field_id;
            productConfigs[stage][idx] = fieldData;
        }
    } else {
        if (!productConfigs[stage]) {
            productConfigs[stage] = [];
        }
        productConfigs[stage].push(fieldData);
    }

    closeFieldModal();
    renderConfigEditor();
}

function deleteConfigField(stage, index) {
    if (!confirm('确定要删除该字段吗？')) return;
    if (productConfigs[stage]) {
        productConfigs[stage].splice(index, 1);
        if (productConfigs[stage].length === 0) {
            delete productConfigs[stage];
        }
        renderConfigEditor();
    }
}

function saveProductConfig() {
    if (!selectedConfigProductId) {
        alert('请先选择产品');
        return;
    }

    var stages = ["原材料获取", "生产制造", "运输交付", "使用阶段", "维护保养", "报废回收"];
    var savePromises = [];

    stages.forEach(function(stage) {
        var config = productConfigs[stage] || [];
        var promise = fetch('/api/product_config', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                product_id: selectedConfigProductId,
                stage: stage,
                config: config
            })
        });
        savePromises.push(promise);
    });

    Promise.all(savePromises)
    .then(function() {
        alert('✅ 配置保存成功！');
        loadConfigForEdit(selectedConfigProductId);
    })
    .catch(function(e) {
        alert('❌ 保存失败: ' + e.message);
    });
}

function addConfigField() {
    if (!selectedConfigProductId) {
        alert('请先选择产品');
        return;
    }
    var stages = ["原材料获取", "生产制造", "运输交付", "使用阶段", "维护保养", "报废回收"];
    openFieldModal(stages[0]);
}

// ============================================================
// 产品信息管理
// ============================================================

function loadProductList() {
    var area = document.getElementById('productListArea');
    if (!area) return;
    area.innerHTML = '<div style="text-align:center; color:#95a5a6; padding:20px; font-size:13px;">⏳ 加载中...</div>';

    fetch('/api/all_products')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (!Array.isArray(data)) {
            if (data && data.data && Array.isArray(data.data)) {
                data = data.data;
            } else if (data && typeof data === 'object') {
                data = [data];
            } else {
                data = [];
            }
        }

        var countEl = document.getElementById('productCountInfo');
        if (countEl) countEl.textContent = '共 ' + data.length + ' 种产品';

        area.innerHTML = '';
        if (data.length === 0) {
            area.innerHTML = '<div style="text-align:center; color:#95a5a6; padding:40px 0; font-size:13px;">📌 暂无产品，点击"新增产品"添加</div>';
            return;
        }

        var tableWrap = document.createElement('div');
        tableWrap.className = 'product-table-wrap';

        var table = document.createElement('table');
        table.className = 'product-table';

        var thead = document.createElement('thead');
        var headerRow = document.createElement('tr');

        var headers = [
            '序号', '产品名称', '产品编码', '产品型号', '规格型号',
            '分类', '单位', '功能单位', '声明单位', '设计寿命', '参考标准', '操作'
        ];
        var colWidths = ['40px', '120px', '100px', '100px', '120px', '80px', '60px', '120px', '100px', '80px', '100px', '140px'];

        headers.forEach(function(h, idx) {
            var th = document.createElement('th');
            th.textContent = h;
            th.style.minWidth = colWidths[idx];
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);

        var tbody = document.createElement('tbody');

        data.forEach(function(product, index) {
            var tr = document.createElement('tr');

            var rowData = [
                index + 1,
                product.product_name || '-',
                product.product_code || '-',
                product.product_model || '-',
                product.specification || '-',
                product.category_name || '-',
                product.unit || '-',
                product.functional_unit || '-',
                product.declared_unit || '-',
                product.design_life || '-',
                product.reference_standard || '-'
            ];

            rowData.forEach(function(value) {
                var td = document.createElement('td');
                td.textContent = value;
                if (value === '-') {
                    td.className = 'empty-value';
                }
                tr.appendChild(td);
            });

            // 操作列
            var actionTd = document.createElement('td');

            var editBtn = document.createElement('button');
            editBtn.textContent = '✏️';
            editBtn.title = '编辑';
            editBtn.className = 'action-btn edit';
            editBtn.onclick = function(e) {
                e.stopPropagation();
                openProductModal(product);
            };
            actionTd.appendChild(editBtn);

            var delBtn = document.createElement('button');
            delBtn.textContent = '🗑️';
            delBtn.title = '删除';
            delBtn.className = 'action-btn delete';
            delBtn.onclick = function(e) {
                e.stopPropagation();
                if (confirm('确定要删除产品 "' + (product.product_name || '') + '" 吗？')) {
                    deleteProduct(product.id);
                }
            };
            actionTd.appendChild(delBtn);

            tr.appendChild(actionTd);

            tr.onclick = function() {
                switchTab('calculator');
                setTimeout(function() {
                    var treeItems = document.querySelectorAll('#productTree .product-tree-item');
                    treeItems.forEach(function(item) {
                        if (parseInt(item.dataset.id) === product.id) {
                            item.click();
                        }
                    });
                }, 300);
            };

            tbody.appendChild(tr);
        });

        table.appendChild(tbody);
        tableWrap.appendChild(table);
        area.appendChild(tableWrap);

        var note = document.createElement('div');
        note.className = 'product-table-note';
        note.innerHTML = '💡 点击行可跳转到"碳足迹核算"页面，点击 ✏️ 编辑产品信息，点击 🗑️ 删除产品。';
        area.appendChild(note);
    })
    .catch(function(e) {
        console.error('❌ 加载产品列表失败:', e);
        area.innerHTML = '<div style="text-align:center; color:#e74c3c; padding:20px; font-size:13px;">❌ 加载失败: ' + e.message + '</div>';
    });
}

function openProductModal(product) {
    var modal = document.getElementById('productModal');
    if (!modal) return;
    var title = document.getElementById('productModalTitle');
    var editId = document.getElementById('editProductId');

    loadCategorySelect();

    if (product) {
        title.textContent = '编辑产品';
        editId.value = product.id || '';
        document.getElementById('productName').value = product.product_name || '';
        document.getElementById('productCategory').value = product.category_id || '';
        document.getElementById('productCode').value = product.product_code || '';
        document.getElementById('productModel').value = product.product_model || '';
        document.getElementById('productSpec').value = product.specification || '';
        document.getElementById('productUnit').value = product.unit || '';
        document.getElementById('functionalUnit').value = product.functional_unit || '';
        document.getElementById('declaredUnit').value = product.declared_unit || '';
        document.getElementById('designLife').value = product.design_life || '';
        document.getElementById('referenceStandard').value = product.reference_standard || '';
        document.getElementById('productDesc').value = product.description || '';
    } else {
        title.textContent = '新增产品';
        editId.value = '';
        document.getElementById('productName').value = '';
        document.getElementById('productCategory').value = '';
        document.getElementById('productCode').value = '';
        document.getElementById('productModel').value = '';
        document.getElementById('productSpec').value = '';
        document.getElementById('productUnit').value = '';
        document.getElementById('functionalUnit').value = '';
        document.getElementById('declaredUnit').value = '';
        document.getElementById('designLife').value = '';
        document.getElementById('referenceStandard').value = '';
        document.getElementById('productDesc').value = '';
    }

    modal.style.display = 'flex';
}

function closeProductModal() {
    var modal = document.getElementById('productModal');
    if (modal) modal.style.display = 'none';
}

function loadCategorySelect() {
    var select = document.getElementById('productCategory');
    if (!select) return;
    fetch('/api/product_categories')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        var currentVal = select.value;
        select.innerHTML = '<option value="">请选择分类</option>';
        if (Array.isArray(data)) {
            data.forEach(function(cat) {
                var opt = document.createElement('option');
                opt.value = cat.id;
                opt.textContent = (cat.icon || '📁') + ' ' + cat.category_name;
                if (cat.id == currentVal) opt.selected = true;
                select.appendChild(opt);
            });
        }
    })
    .catch(function(e) {
        console.error('加载分类失败:', e);
    });
}

function saveProduct() {
    var id = document.getElementById('editProductId').value;
    var name = document.getElementById('productName').value.trim();
    var categoryId = document.getElementById('productCategory').value;

    if (!name) {
        alert('请输入产品名称');
        return;
    }
    if (!categoryId) {
        alert('请选择产品分类');
        return;
    }

    var data = {
        product_name: name,
        category_id: parseInt(categoryId),
        product_code: document.getElementById('productCode').value.trim(),
        product_model: document.getElementById('productModel').value.trim(),
        specification: document.getElementById('productSpec').value.trim(),
        unit: document.getElementById('productUnit').value.trim(),
        functional_unit: document.getElementById('functionalUnit').value.trim(),
        declared_unit: document.getElementById('declaredUnit').value.trim(),
        design_life: document.getElementById('designLife').value.trim(),
        reference_standard: document.getElementById('referenceStandard').value.trim(),
        description: document.getElementById('productDesc').value.trim(),
        sort_order: 0
    };

    var url = '/api/products';
    var method = 'POST';
    if (id) {
        url = '/api/products/' + id;
        method = 'PUT';
    }

    fetch(url, {
        method: method,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(function(response) { return response.json(); })
    .then(function(result) {
        if (result.success) {
            alert(result.message);
            closeProductModal();
            loadProductList();
            renderProductTree('productTree', handleProductSelect);
            renderProductTree('configTree', handleConfigSelect);
        } else {
            alert('操作失败: ' + (result.error || '未知错误'));
        }
    })
    .catch(function(e) {
        alert('请求失败: ' + e.message);
    });
}

function deleteProduct(productId) {
    fetch('/api/products/' + productId, {
        method: 'DELETE',
        headers: {'Content-Type': 'application/json'}
    })
    .then(function(response) { return response.json(); })
    .then(function(result) {
        if (result.success) {
            alert(result.message);
            loadProductList();
            renderProductTree('productTree', handleProductSelect);
            renderProductTree('configTree', handleConfigSelect);
        } else {
            alert('删除失败: ' + (result.error || '未知错误'));
        }
    })
    .catch(function(e) {
        alert('请求失败: ' + e.message);
    });
}

// ============================================================
// 刷新树
// ============================================================
function refreshProductTree() {
    renderProductTree('productTree', handleProductSelect);
}

function refreshConfigTree() {
    renderProductTree('configTree', handleConfigSelect);
}

// ============================================================
// 页面初始化
// ============================================================
document.addEventListener('DOMContentLoaded', function() {
    renderProductTree('productTree', handleProductSelect);
    renderProductTree('overviewTree', handleOverviewSelect);
    loadCategorySelect();
    onOverviewPeriodChange();
    onCalculatorPeriodChange();
});
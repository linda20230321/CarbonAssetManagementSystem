// static/js/organization.js

// ============================================================
// 全局状态变量
// ============================================================

let currentOrgId = null;
let currentOrgName = '';
let sourceSelections = {};
let inputValues = {};
let calculationResults = {};
let calculationMethodsData = [];

// ============================================================
// 排放源数据（固定数据）
// ============================================================

const EMISSION_SOURCES_LIST = [
    {id: 1, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '无烟煤', unit: '吨', default_factor: 2.32},
    {id: 2, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '烟煤', unit: '吨', default_factor: 2.07},
    {id: 3, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '煤制品', unit: '吨', default_factor: 1.94},
    {id: 4, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '焦炭', unit: '吨', default_factor: 2.85},
    {id: 5, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '褐煤', unit: '吨', default_factor: 1.42},
    {id: 6, range: '范围1', scenario: '牵引排放', source_type: '固体燃料', name: '洗精煤', unit: '吨', default_factor: 2.28},
    {id: 7, range: '范围1', scenario: '牵引排放', source_type: '液体燃料', name: '燃料油（重油）', unit: '吨', default_factor: 3.05},
    {id: 8, range: '范围1', scenario: '牵引排放', source_type: '液体燃料', name: '柴油', unit: '吨', default_factor: 3.15},
    {id: 9, range: '范围1', scenario: '牵引排放', source_type: '液体燃料', name: '汽油', unit: '吨', default_factor: 3.04},
    {id: 10, range: '范围1', scenario: '牵引排放', source_type: '液体燃料', name: '煤油', unit: '吨', default_factor: 3.15},
    {id: 11, range: '范围1', scenario: '牵引排放', source_type: '气体燃料', name: '焦炉煤气', unit: '万Nm³', default_factor: 8.58},
    {id: 12, range: '范围1', scenario: '牵引排放', source_type: '气体燃料', name: '油田天然气', unit: '万Nm³', default_factor: 21.62},
    {id: 13, range: '范围1', scenario: '牵引排放', source_type: '气体燃料', name: '气田天然气', unit: '万Nm³', default_factor: 19.74},
    {id: 14, range: '范围1', scenario: '牵引排放', source_type: '气体燃料', name: '液化石油气', unit: '吨', default_factor: 2.95},
    {id: 15, range: '范围1', scenario: '牵引排放', source_type: '气体燃料', name: '液化天然气', unit: '吨', default_factor: 2.33},
    {id: 16, range: '范围1', scenario: '非牵引排放', source_type: '固定源燃烧', name: '办公室供暖', unit: 'GJ', default_factor: 0.11},
    {id: 17, range: '范围1', scenario: '非牵引排放', source_type: '固定源燃烧', name: '发电机', unit: 'kWh', default_factor: 0.0005},
    {id: 18, range: '范围1', scenario: '非牵引排放', source_type: '固定源燃烧', name: '其他固定燃烧', unit: 'GJ', default_factor: 0.11},
    {id: 19, range: '范围1', scenario: '非牵引排放', source_type: '移动源燃烧', name: '道路车辆及机械', unit: '升', default_factor: 0.0027},
    {id: 20, range: '范围1', scenario: '非牵引排放', source_type: '装卸设备', name: '专业装卸设备', unit: 'kWh', default_factor: 0.0005},
    {id: 21, range: '范围2', scenario: '牵引排放', source_type: '购电', name: '电动列车用电', unit: 'MWh', default_factor: 0.5366},
    {id: 22, range: '范围2', scenario: '非牵引排放', source_type: '外购电力', name: '道路车辆用电', unit: 'MWh', default_factor: 0.5366},
    {id: 23, range: '范围2', scenario: '非牵引排放', source_type: '外购电力', name: '装卸设备用电', unit: 'MWh', default_factor: 0.5366},
    {id: 24, range: '范围2', scenario: '非牵引排放', source_type: '外购电力', name: '办公室及仓库用电', unit: 'MWh', default_factor: 0.5366},
    {id: 25, range: '范围2', scenario: '非牵引排放', source_type: '外购热力', name: '外购热力', unit: 'GJ', default_factor: 0.11},
    {id: 26, range: '范围3', scenario: '采购的货物和服务', source_type: '铁路车辆', name: '铁路车辆维护承包商', unit: '次', default_factor: 0.05},
    {id: 27, range: '范围3', scenario: '采购的货物和服务', source_type: '铁路车辆', name: '铁路车辆部件', unit: '件', default_factor: 0.05},
    {id: 28, range: '范围3', scenario: '采购的货物和服务', source_type: '铁路车辆', name: '油品润滑剂', unit: '升', default_factor: 0.0027},
    {id: 29, range: '范围3', scenario: '采购的货物和服务', source_type: '装卸设备', name: '设备部件', unit: '件', default_factor: 0.05},
    {id: 30, range: '范围3', scenario: '采购的货物和服务', source_type: '装卸设备', name: '装卸设备油品', unit: '升', default_factor: 0.0027},
    {id: 31, range: '范围3', scenario: '采购的货物和服务', source_type: '建筑物', name: '清洁服务', unit: '次', default_factor: 0.02},
    {id: 32, range: '范围3', scenario: '采购的货物和服务', source_type: '建筑物', name: '办公用品', unit: '件', default_factor: 0.01},
    {id: 33, range: '范围3', scenario: '采购的货物和服务', source_type: 'IT和电信', name: '数据中心服务', unit: '月', default_factor: 0.5},
    {id: 34, range: '范围3', scenario: '采购的货物和服务', source_type: 'IT和电信', name: '电信服务', unit: '月', default_factor: 0.3},
    {id: 35, range: '范围3', scenario: '资本货物', source_type: '铁路车辆', name: '新机车车辆', unit: '辆', default_factor: 50},
    {id: 36, range: '范围3', scenario: '资本货物', source_type: '装卸设备', name: '新装卸设备', unit: '台', default_factor: 10},
    {id: 37, range: '范围3', scenario: '资本货物', source_type: '道路车辆和机械', name: '新道路车辆', unit: '辆', default_factor: 15},
    {id: 38, range: '范围3', scenario: '资本货物', source_type: '建筑物', name: '新建筑物', unit: '平方米', default_factor: 0.5},
    {id: 39, range: '范围3', scenario: '燃料和能源相关活动', source_type: '第三方', name: '燃油燃油税', unit: '吨', default_factor: 0.1},
    {id: 40, range: '范围3', scenario: '燃料和能源相关活动', source_type: '第三方', name: '电力WTT', unit: 'MWh', default_factor: 0.05},
    {id: 41, range: '范围3', scenario: '燃料和能源相关活动', source_type: '第三方', name: '输配电损耗', unit: 'MWh', default_factor: 0.02},
    {id: 42, range: '范围3', scenario: '商务差旅', source_type: '商务差旅', name: '商务旅行(陆路)', unit: '公里', default_factor: 0.00025},
    {id: 43, range: '范围3', scenario: '商务差旅', source_type: '商务差旅', name: '商务旅行(航空)', unit: '公里', default_factor: 0.00015},
    {id: 44, range: '范围3', scenario: '商务差旅', source_type: '商务差旅', name: '酒店住宿', unit: '晚', default_factor: 0.02},
    {id: 45, range: '范围3', scenario: '员工通勤', source_type: '员工通勤', name: '员工通勤', unit: '公里', default_factor: 0.00015},
    {id: 46, range: '范围3', scenario: '员工通勤', source_type: '员工通勤', name: '在家办公', unit: '天', default_factor: 0.01}
];

// ============================================================
// 组织数据
// ============================================================

const ORG_DATA = [
    {
        id: 1,
        name: '国铁集团',
        level: 1,
        children: [
            {
                id: 2,
                name: '铁路局集团公司',
                level: 2,
                children: [
                    {id: 3, name: '哈尔滨局', level: 3},
                    {id: 4, name: '沈阳局', level: 3},
                    {id: 5, name: '北京局', level: 3},
                    {id: 6, name: '上海局', level: 3},
                    {id: 7, name: '广州局', level: 3},
                    {id: 8, name: '成都局', level: 3},
                    {id: 9, name: '武汉局', level: 3},
                    {id: 10, name: '西安局', level: 3},
                    {id: 11, name: '济南局', level: 3},
                    {id: 12, name: '南昌局', level: 3}
                ]
            },
            {
                id: 13,
                name: '专业运输公司',
                level: 2,
                children: [
                    {id: 14, name: '中铁集装箱', level: 3},
                    {id: 15, name: '中铁特货运输', level: 3},
                    {id: 16, name: '中铁快运股份', level: 3}
                ]
            },
            {
                id: 17,
                name: '非运输企业',
                level: 2,
                children: [
                    {id: 18, name: '中国铁投', level: 3},
                    {id: 19, name: '铁科院', level: 3},
                    {id: 20, name: '经规院', level: 3}
                ]
            },
            {
                id: 21,
                name: '事业单位',
                level: 2,
                children: [
                    {id: 22, name: '铁道党校', level: 3},
                    {id: 23, name: '中国铁道博物馆', level: 3}
                ]
            },
            {
                id: 24,
                name: '合资公司',
                level: 2,
                children: [
                    {id: 25, name: '京沪高铁', level: 3},
                    {id: 26, name: '长江沿岸', level: 3},
                    {id: 27, name: '云桂铁路', level: 3}
                ]
            }
        ]
    }
];


// ============================================================
// DOM 加载完成
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ organization.js 已加载');
    initAllTrees();
});


// ============================================================
// 标签页切换
// ============================================================

function switchOrgTab(tab) {
    document.querySelectorAll('.tab-btn').forEach(function(btn) {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    document.querySelectorAll('.org-tab-content').forEach(function(el) {
        el.style.display = 'none';
    });

    var target = document.getElementById('tab-' + tab);
    if (target) {
        target.style.display = 'flex';
    }

    if (tab === 'source' || tab === 'input') {
        if (!currentOrgId) {
            var firstNode = document.querySelector('#sourceTree .tree-node-item');
            if (firstNode) firstNode.click();
        } else {
            loadOrgConfig(currentOrgId);
        }
    }
    if (tab === 'result') {
        if (!currentOrgId) {
            var firstNode = document.querySelector('#resultTree .tree-node-item');
            if (firstNode) firstNode.click();
        } else {
            loadResultsFromDB(currentOrgId);
        }
    }
    if (tab === 'detail') {
        if (!currentOrgId) {
            var firstNode = document.querySelector('#detailTree .tree-node-item');
            if (firstNode) firstNode.click();
        } else {
            loadResultsFromDB(currentOrgId);
        }
    }
    if (tab === 'trend') {
        if (!currentOrgId) {
            var firstNode = document.querySelector('#trendTree .tree-node-item');
            if (firstNode) firstNode.click();
        } else {
            loadResultsFromDB(currentOrgId);
            drawTrendChart();
        }
    }
    if (tab === 'method') loadCalculationMethods();
}


// ============================================================
// 组织树渲染
// ============================================================

function renderTree(containerId, data, onSelect) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    function buildTree(nodes, level, parentContainer) {
        nodes.forEach(function(node) {
            var div = document.createElement('div');
            div.className = 'tree-node-item';
            div.style.padding = '2px 4px 2px ' + (level * 16 + 4) + 'px';
            div.style.cursor = 'pointer';
            div.style.borderRadius = '3px';
            div.style.display = 'flex';
            div.style.alignItems = 'center';
            div.style.gap = '3px';
            div.style.fontSize = '13px';
            div.style.lineHeight = '1.5';
            div.dataset.id = node.id;
            div.dataset.name = node.name;
            div.dataset.level = node.level;

            if (node.children && node.children.length > 0) {
                var toggle = document.createElement('span');
                toggle.textContent = '▼';
                toggle.style.fontSize = '10px';
                toggle.style.cursor = 'pointer';
                toggle.style.width = '14px';
                toggle.style.display = 'inline-block';
                toggle.className = 'tree-toggle-btn';
                toggle.onclick = function(e) {
                    e.stopPropagation();
                    var childContainer = this.closest('.tree-node-item').querySelector('.tree-children-container');
                    if (childContainer) {
                        if (childContainer.style.display === 'none') {
                            childContainer.style.display = 'block';
                            this.textContent = '▼';
                        } else {
                            childContainer.style.display = 'none';
                            this.textContent = '▶';
                        }
                    }
                };
                div.appendChild(toggle);
            } else {
                var spacer = document.createElement('span');
                spacer.style.display = 'inline-block';
                spacer.style.width = '14px';
                div.appendChild(spacer);
            }

            var icon = node.level === 1 ? '🏢' : node.level === 2 ? '📁' : '•';
            var label = document.createElement('span');
            label.textContent = icon + ' ' + node.name;
            div.appendChild(label);

            div.onclick = function(e) {
                if (e.target.classList.contains('tree-toggle-btn')) return;
                document.querySelectorAll('#' + containerId + ' .tree-node-item').forEach(function(el) {
                    el.style.background = 'transparent';
                });
                div.style.background = '#e8f4fd';
                if (onSelect) onSelect(node);
            };

            parentContainer.appendChild(div);

            if (node.children && node.children.length > 0) {
                var childContainer = document.createElement('div');
                childContainer.className = 'tree-children-container';
                childContainer.style.display = 'block';
                parentContainer.appendChild(childContainer);
                buildTree(node.children, level + 1, childContainer);
            }
        });
    }
    buildTree(data, 0, container);
}


// ============================================================
// 初始化所有组织树
// ============================================================

function initAllTrees() {
    console.log('🔧 初始化组织树...');

    renderTree('sourceTree', ORG_DATA, function(node) {
        currentOrgId = node.id;
        currentOrgName = node.name;
        document.getElementById('sourceOrgName').textContent = node.name;
        loadOrgConfig(node.id);
    });

    renderTree('inputTree', ORG_DATA, function(node) {
        currentOrgId = node.id;
        currentOrgName = node.name;
        document.getElementById('inputOrgName').textContent = node.name;
        loadOrgConfig(node.id);
    });

    renderTree('resultTree', ORG_DATA, function(node) {
        currentOrgId = node.id;
        currentOrgName = node.name;
        document.getElementById('resultOrgName').textContent = node.name;
        loadResultsFromDB(node.id);
    });

    renderTree('detailTree', ORG_DATA, function(node) {
        currentOrgId = node.id;
        currentOrgName = node.name;
        document.getElementById('detailOrgName').textContent = node.name;
        loadResultsFromDB(node.id);
    });

    renderTree('trendTree', ORG_DATA, function(node) {
        currentOrgId = node.id;
        currentOrgName = node.name;
        document.getElementById('trendOrgName').textContent = node.name;
        loadResultsFromDB(node.id);
        drawTrendChart();
    });

    setTimeout(function() {
        var firstNode = document.querySelector('#sourceTree .tree-node-item');
        if (firstNode) {
            console.log('🔧 自动点击第一个节点');
            firstNode.click();
        } else {
            console.log('⚠️ 没有找到节点，手动加载哈尔滨局');
            currentOrgId = 3;
            currentOrgName = '哈尔滨局';
            document.getElementById('sourceOrgName').textContent = '哈尔滨局';
            loadOrgConfig(3);
        }
    }, 500);
}


// ============================================================
// 展开/折叠
// ============================================================

function expandAllTree(treeId) {
    var container = document.getElementById(treeId);
    if (!container) return;
    container.querySelectorAll('.tree-children-container').forEach(function(el) {
        el.style.display = 'block';
    });
    container.querySelectorAll('.tree-toggle-btn').forEach(function(el) {
        el.textContent = '▼';
    });
}

function collapseAllTree(treeId) {
    var container = document.getElementById(treeId);
    if (!container) return;
    container.querySelectorAll('.tree-children-container').forEach(function(el) {
        el.style.display = 'none';
    });
    container.querySelectorAll('.tree-toggle-btn').forEach(function(el) {
        el.textContent = '▶';
    });
}


// ============================================================
// 保存排放源配置到数据库
// ============================================================

function saveSourceConfigToDB() {
    if (!currentOrgId) {
        return Promise.resolve(false);
    }

    var data = {
        org_id: currentOrgId,
        org_name: currentOrgName,
        selections: sourceSelections
    };

    return fetch('/api/source_configs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(function(response) {
        if (response.ok) {
            console.log('✅ 组织 ' + currentOrgName + ' 的排放源配置已保存');
            return true;
        }
        return false;
    })
    .catch(function(e) {
        console.log('保存失败:', e);
        return false;
    });
}


// ============================================================
// 加载组织配置
// ============================================================

function loadOrgConfig(orgId) {
    if (!orgId) return;

    console.log('📂 加载组织 ' + orgId + ' 的配置');

    fetch('/api/source_configs/' + orgId)
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        console.log('📥 加载到的数据:', data);

        sourceSelections = {};

        if (data && Object.keys(data).length > 0) {
            for (var key in data) {
                if (data.hasOwnProperty(key)) {
                    sourceSelections[key] = data[key];
                }
            }
            console.log('✅ 从数据库加载了 ' + Object.keys(data).length + ' 个排放源配置');
        } else {
            console.log('⚠️ 数据库无配置，使用默认全选');
            for (var i = 0; i < EMISSION_SOURCES_LIST.length; i++) {
                var s = EMISSION_SOURCES_LIST[i];
                var k = s.id + '_' + s.name;
                sourceSelections[k] = true;
            }
        }

        renderSourceConfigUI();
        renderInputUI();

        console.log('✅ 组织 ' + orgId + ' 配置加载完成');
    })
    .catch(function(e) {
        console.error('❌ 加载组织配置失败:', e);
        for (var j = 0; j < EMISSION_SOURCES_LIST.length; j++) {
            var s2 = EMISSION_SOURCES_LIST[j];
            var k2 = s2.id + '_' + s2.name;
            sourceSelections[k2] = true;
        }
        renderSourceConfigUI();
        renderInputUI();
    });
}


// ============================================================
// 渲染排放源配置UI
// ============================================================

function renderSourceConfigUI() {
    console.log('🔧 开始渲染排放源配置UI');

    var range1 = EMISSION_SOURCES_LIST.filter(function(s) { return s.range === '范围1'; });
    var range2 = EMISSION_SOURCES_LIST.filter(function(s) { return s.range === '范围2'; });
    var range3 = EMISSION_SOURCES_LIST.filter(function(s) { return s.range === '范围3'; });

    renderSourceGroup('sourceRange1', range1);
    renderSourceGroup('sourceRange2', range2);
    renderSourceGroup('sourceRange3', range3);

    console.log('✅ 排放源配置UI渲染完成');
}

function renderSourceGroup(containerId, sources) {
    var container = document.getElementById(containerId);
    if (!container) {
        console.log('❌ 容器 ' + containerId + ' 不存在');
        return;
    }

    container.innerHTML = '';

    var scenarios = {};
    for (var i = 0; i < sources.length; i++) {
        var s = sources[i];
        if (!scenarios[s.scenario]) {
            scenarios[s.scenario] = [];
        }
        scenarios[s.scenario].push(s);
    }

    for (var scenario in scenarios) {
        if (!scenarios.hasOwnProperty(scenario)) continue;
        var items = scenarios[scenario];

        var scenarioDiv = document.createElement('div');
        scenarioDiv.style.marginBottom = '6px';

        var title = document.createElement('div');
        title.textContent = scenario;
        title.style.fontWeight = 'bold';
        title.style.fontSize = '13px';
        title.style.color = '#2c3e50';
        title.style.marginBottom = '4px';
        scenarioDiv.appendChild(title);

        for (var j = 0; j < items.length; j++) {
            var s2 = items[j];
            var key = s2.id + '_' + s2.name;

            var row = document.createElement('div');
            row.style.display = 'flex';
            row.style.alignItems = 'center';
            row.style.gap = '6px';
            row.style.padding = '3px 0';
            row.style.fontSize = '13px';
            row.style.paddingLeft = '10px';

            var cb = document.createElement('input');
            cb.type = 'checkbox';
            cb.className = 'source-checkbox';
            cb.dataset.key = key;

            if (sourceSelections[key] !== undefined) {
                cb.checked = sourceSelections[key];
            } else {
                cb.checked = true;
                sourceSelections[key] = true;
            }

            (function(k) {
                cb.onchange = function() {
                    sourceSelections[k] = this.checked;
                    renderInputUI();
                    saveSourceConfigToDB();
                };
            })(key);

            row.appendChild(cb);

            var label = document.createElement('span');
            label.textContent = s2.name + ' (' + s2.unit + ')';
            label.style.flex = '1';
            row.appendChild(label);

            scenarioDiv.appendChild(row);
        }

        container.appendChild(scenarioDiv);
    }
}


// ============================================================
// 渲染输入页面UI
// ============================================================

function renderInputUI() {
    var selectedSources = EMISSION_SOURCES_LIST.filter(function(s) {
        var key = s.id + '_' + s.name;
        return sourceSelections[key] === true;
    });

    var range1 = selectedSources.filter(function(s) { return s.range === '范围1'; });
    var range2 = selectedSources.filter(function(s) { return s.range === '范围2'; });
    var range3 = selectedSources.filter(function(s) { return s.range === '范围3'; });

    renderInputGroup('inputRange1', range1);
    renderInputGroup('inputRange2', range2);
    renderInputGroup('inputRange3', range3);

    var inputs = document.querySelectorAll('.input-range input[type="number"]');
    for (var i = 0; i < inputs.length; i++) {
        var input = inputs[i];
        var key = input.dataset.key;
        if (key && inputValues[key] !== undefined && inputValues[key] > 0) {
            input.value = inputValues[key];
        }
    }
}

function renderInputGroup(containerId, sources) {
    var container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    if (sources.length === 0) {
        var empty = document.createElement('div');
        empty.textContent = '暂无排放源，请先在排放源配置中选择';
        empty.style.color = '#95a5a6';
        empty.style.textAlign = 'center';
        empty.style.padding = '20px';
        empty.style.fontSize = '13px';
        container.appendChild(empty);
        return;
    }

    for (var i = 0; i < sources.length; i++) {
        var s = sources[i];
        var key = s.id + '_' + s.name;

        var row = document.createElement('div');
        row.className = 'input-range';
        row.style.display = 'flex';
        row.style.alignItems = 'center';
        row.style.gap = '6px';
        row.style.padding = '4px 0';
        row.style.borderBottom = '1px solid #f0f0f0';
        row.style.fontSize = '13px';

        var label = document.createElement('span');
        label.textContent = s.name;
        label.style.flex = '1';
        label.style.fontWeight = '500';
        row.appendChild(label);

        var unitLabel = document.createElement('span');
        unitLabel.textContent = s.unit;
        unitLabel.style.fontSize = '12px';
        unitLabel.style.color = '#7f8c8d';
        unitLabel.style.width = '40px';
        row.appendChild(unitLabel);

        var input = document.createElement('input');
        input.type = 'number';
        input.step = '0.01';
        input.style.width = '70px';
        input.style.padding = '2px 6px';
        input.style.border = '1px solid #d0d7de';
        input.style.borderRadius = '3px';
        input.style.fontSize = '13px';
        input.style.textAlign = 'right';
        input.dataset.key = key;
        if (inputValues[key] !== undefined && inputValues[key] > 0) {
            input.value = inputValues[key];
        } else {
            input.value = 0;
        }
        (function(k) {
            input.onchange = function() {
                inputValues[k] = parseFloat(this.value) || 0;
            };
        })(key);
        row.appendChild(input);

        container.appendChild(row);
    }
}


// ============================================================
// 兼容旧函数
// ============================================================

function loadSourceConfig() {
    renderSourceConfigUI();
}

function loadInputData() {
    renderInputUI();
}


// ============================================================
// 全选/取消全选
// ============================================================

function selectAllRange(rangeId) {
    var containerId = 'sourceRange' + (rangeId === 'range1' ? '1' : rangeId === 'range2' ? '2' : '3');
    var container = document.getElementById(containerId);
    if (container) {
        var cbs = container.querySelectorAll('.source-checkbox');
        for (var i = 0; i < cbs.length; i++) {
            cbs[i].checked = true;
            sourceSelections[cbs[i].dataset.key] = true;
        }
        renderInputUI();
        saveSourceConfigToDB();
    }
}

function deselectAllRange(rangeId) {
    var containerId = 'sourceRange' + (rangeId === 'range1' ? '1' : rangeId === 'range2' ? '2' : '3');
    var container = document.getElementById(containerId);
    if (container) {
        var cbs = container.querySelectorAll('.source-checkbox');
        for (var i = 0; i < cbs.length; i++) {
            cbs[i].checked = false;
            sourceSelections[cbs[i].dataset.key] = false;
        }
        renderInputUI();
        saveSourceConfigToDB();
    }
}


// ============================================================
// 保存排放源配置（手动保存按钮）
// ============================================================

function saveSourceConfig() {
    if (!currentOrgId) {
        alert('请先选择组织');
        return;
    }

    var cbs = document.querySelectorAll('.source-checkbox');
    for (var i = 0; i < cbs.length; i++) {
        var key = cbs[i].dataset.key;
        if (key) {
            sourceSelections[key] = cbs[i].checked;
        }
    }

    var selectedCount = 0;
    for (var k in sourceSelections) {
        if (sourceSelections[k] === true) selectedCount++;
    }

    saveSourceConfigToDB().then(function(success) {
        if (success) {
            alert('✅ 排放源配置保存成功！共选中 ' + selectedCount + ' 个排放源');
            renderInputUI();
        } else {
            alert('❌ 保存失败，请检查网络连接');
        }
    });
}


// ============================================================
// 周期变化
// ============================================================

function onInputPeriodChange() {
    var period = document.getElementById('inputPeriod').value;
    var detail = document.getElementById('inputPeriodDetail');
    detail.innerHTML = '';

    if (period === '月度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="inputYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">月份</label>
                <select id="inputMonth" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="1">1月</option><option value="2">2月</option><option value="3">3月</option>
                    <option value="4">4月</option><option value="5">5月</option><option value="6">6月</option>
                    <option value="7">7月</option><option value="8">8月</option><option value="9">9月</option>
                    <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
                </select>
            </div>
        `;
    } else if (period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="inputYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">季度</label>
                <select id="inputQuarter" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="Q1">Q1</option><option value="Q2">Q2</option><option value="Q3">Q3</option><option value="Q4">Q4</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="inputYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
        `;
    } else {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">开始</label>
                <input type="date" id="inputStart" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-01-01">
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">结束</label>
                <input type="date" id="inputEnd" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-12-31">
            </div>
        `;
    }
}

function onResultPeriodChange() {
    var period = document.getElementById('resultPeriodType').value;
    var detail = document.getElementById('resultPeriodDetail');
    detail.innerHTML = '';

    if (period === '月度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="resultYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">月份</label>
                <select id="resultMonth" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="1">1月</option><option value="2">2月</option><option value="3">3月</option>
                    <option value="4">4月</option><option value="5">5月</option><option value="6">6月</option>
                    <option value="7">7月</option><option value="8">8月</option><option value="9">9月</option>
                    <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
                </select>
            </div>
        `;
    } else if (period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="resultYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">季度</label>
                <select id="resultQuarter" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="Q1">Q1</option><option value="Q2">Q2</option><option value="Q3">Q3</option><option value="Q4">Q4</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="resultYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
        `;
    } else {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">开始</label>
                <input type="date" id="resultStart" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-01-01">
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">结束</label>
                <input type="date" id="resultEnd" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-12-31">
            </div>
        `;
    }
}

function onDetailPeriodChange() {
    var period = document.getElementById('detailPeriodType').value;
    var detail = document.getElementById('detailPeriodDetail');
    detail.innerHTML = '';

    if (period === '月度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="detailYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">月份</label>
                <select id="detailMonth" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="1">1月</option><option value="2">2月</option><option value="3">3月</option>
                    <option value="4">4月</option><option value="5">5月</option><option value="6">6月</option>
                    <option value="7">7月</option><option value="8">8月</option><option value="9">9月</option>
                    <option value="10">10月</option><option value="11">11月</option><option value="12">12月</option>
                </select>
            </div>
        `;
    } else if (period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="detailYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">季度</label>
                <select id="detailQuarter" class="form-control" style="width:60px; font-size:13px; padding:3px 6px;">
                    <option value="Q1">Q1</option><option value="Q2">Q2</option><option value="Q3">Q3</option><option value="Q4">Q4</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="detailYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024">2024</option><option value="2023">2023</option><option value="2022">2022</option>
                </select>
            </div>
        `;
    } else {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">开始</label>
                <input type="date" id="detailStart" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-01-01">
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">结束</label>
                <input type="date" id="detailEnd" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-12-31">
            </div>
        `;
    }
}

function onTrendPeriodChange() {
    var period = document.getElementById('trendPeriodType').value;
    var detail = document.getElementById('trendPeriodDetail');
    detail.innerHTML = '';

    if (period === '月度' || period === '季度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">年份</label>
                <select id="trendYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2024" selected>2024</option>
                    <option value="2023">2023</option>
                    <option value="2022">2022</option>
                </select>
            </div>
        `;
    } else if (period === '年度') {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">开始年份</label>
                <select id="trendStartYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2020">2020</option><option value="2021">2021</option>
                    <option value="2022">2022</option><option value="2023">2023</option>
                    <option value="2024">2024</option>
                </select>
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">结束年份</label>
                <select id="trendEndYear" class="form-control" style="width:70px; font-size:13px; padding:3px 6px;">
                    <option value="2020">2020</option><option value="2021">2021</option>
                    <option value="2022">2022</option><option value="2023">2023</option>
                    <option value="2024" selected>2024</option>
                </select>
            </div>
        `;
    } else {
        detail.innerHTML = `
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">开始</label>
                <input type="date" id="trendStart" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-01-01">
            </div>
            <div style="display:flex; flex-direction:column;">
                <label style="font-size:10px; color:#7f8c8d;">结束</label>
                <input type="date" id="trendEnd" class="form-control" style="width:120px; font-size:13px; padding:3px 6px;" value="2024-12-31">
            </div>
        `;
    }
}

function queryResults() {
    if (!currentOrgId) {
        alert('请先选择组织');
        return;
    }
    loadResultsFromDB(currentOrgId);
}

function loadResultsFromDB(orgId) {
    if (!orgId) orgId = currentOrgId;
    if (!orgId) return;

    fetch('/api/energy_data/' + orgId)
    .then(function(response) { return response.json(); })
    .then(function(data) {
        if (data && data.length > 0) {
            var latest = data[0];
            var details = typeof latest.data_json === 'string' ? JSON.parse(latest.data_json) : (latest.data_json || []);
            var total = latest.total_emission || 0;
            document.getElementById('resultValue1').textContent = '0';
            document.getElementById('resultValue2').textContent = '0';
            document.getElementById('resultValue3').textContent = '0';
            document.getElementById('resultTotal').textContent = total.toFixed(2);
        }
    })
    .catch(function(e) { console.log('加载结果失败:', e); });
}

function loadDetailData() {
    if (calculationResults && calculationResults.org_id === currentOrgId && calculationResults.details) {
        updateDetailPage(calculationResults.details, calculationResults.total);
    }
}

function updateDetailPage(details, total) {
    var tbody = document.getElementById('detailBody');
    if (!tbody) return;
    tbody.innerHTML = '';
    if (!details || details.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:20px;color:#95a5a6;">暂无数据</td></tr>';
        document.getElementById('detailTotal').textContent = '总排放量：0 tCO₂';
        return;
    }
    for (var i = 0; i < details.length; i++) {
        var d = details[i];
        var tr = document.createElement('tr');
        tr.style.background = i % 2 === 0 ? '#fafbfc' : 'white';
        tr.innerHTML = '<td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.range + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.source_name + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.unit + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.consumption.toFixed(2) + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.factor + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + d.emission.toFixed(2) + '</td><td style="padding:4px 6px;text-align:center;font-size:13px;">' + (d.percentage || '0') + '%</td>';
        tbody.appendChild(tr);
    }
    document.getElementById('detailTotal').textContent = '总排放量：' + total.toFixed(2) + ' tCO₂';
}

function refreshDetail() {
    if (!currentOrgId) {
        alert('请先选择组织');
        return;
    }
    loadResultsFromDB(currentOrgId);
    alert('✅ 详细数据已刷新');
}

function exportDetail() {
    alert('📥 导出功能开发中');
}

function drawTrendChart() {
    var canvas = document.getElementById('trendCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    canvas.width = canvas.parentElement.clientWidth - 40 || 600;
    canvas.height = 120;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#95a5a6';
    ctx.font = '14px Arial';
    ctx.fillText('趋势图数据请先进行碳核算', 20, 60);
}

function analyzeTrend() {
    if (!currentOrgId) {
        alert('请先选择组织');
        return;
    }
    drawTrendChart();
    alert('✅ 趋势分析完成！');
}


// ============================================================
// 碳核算 - 计算公式
// ============================================================

function calculateEmissions() {
    if (!currentOrgId) {
        alert('请先选择组织');
        return;
    }

    var inputs = document.querySelectorAll('.input-range input[type="number"]');
    for (var i = 0; i < inputs.length; i++) {
        var key = inputs[i].dataset.key;
        if (key) {
            inputValues[key] = parseFloat(inputs[i].value) || 0;
        }
    }

    var results = { '范围1': 0, '范围2': 0, '范围3': 0 };
    var details = [];
    var totalEmission = 0;

    for (var key in inputValues) {
        if (!inputValues.hasOwnProperty(key)) continue;
        var value = inputValues[key];
        if (value > 0) {
            var parts = key.split('_');
            var id = parseInt(parts[0]);
            var source = null;
            for (var j = 0; j < EMISSION_SOURCES_LIST.length; j++) {
                if (EMISSION_SOURCES_LIST[j].id === id) {
                    source = EMISSION_SOURCES_LIST[j];
                    break;
                }
            }
            if (source) {
                var emission = value * source.default_factor;
                results[source.range] += emission;
                totalEmission += emission;
                details.push({
                    source_name: source.name,
                    range: source.range,
                    unit: source.unit,
                    consumption: value,
                    factor: source.default_factor,
                    emission: emission
                });
            }
        }
    }

    for (var d = 0; d < details.length; d++) {
        details[d].percentage = totalEmission > 0 ? (details[d].emission / totalEmission * 100).toFixed(1) : 0;
    }

    calculationResults = {
        org_id: currentOrgId,
        org_name: currentOrgName,
        period: document.getElementById('inputPeriod').value,
        year: parseInt(document.getElementById('inputYear')?.value || 2024),
        month: parseInt(document.getElementById('inputMonth')?.value || 1),
        results: results,
        details: details,
        total: totalEmission,
        calculated_at: new Date().toISOString()
    };

    var msg = '📊 碳核算完成！\n\n';
    msg += '🏢 组织：' + currentOrgName + '\n';
    msg += '📅 周期：' + document.getElementById('inputPeriod').value + '\n';
    msg += '📈 范围1排放：' + results['范围1'].toFixed(2) + ' tCO₂e\n';
    msg += '📈 范围2排放：' + results['范围2'].toFixed(2) + ' tCO₂e\n';
    msg += '📈 范围3排放：' + results['范围3'].toFixed(2) + ' tCO₂e\n';
    msg += '━━━━━━━━━━━━━━━━━━━\n';
    msg += '✅ 总排放量：' + totalEmission.toFixed(2) + ' tCO₂e';

    alert(msg);

    document.getElementById('resultValue1').textContent = results['范围1'].toFixed(2);
    document.getElementById('resultValue2').textContent = results['范围2'].toFixed(2);
    document.getElementById('resultValue3').textContent = results['范围3'].toFixed(2);
    document.getElementById('resultTotal').textContent = totalEmission.toFixed(2);
    updateDetailPage(details, totalEmission);
}


// ============================================================
// 核算方法配置
// ============================================================

var defaultMethods = [
    {id: 1, method_name: '高速铁路客运碳排放量', emission_type: '能源消耗', data_type: '系统默认', is_referenced: 0, is_enabled: 1, unit: 'kgCO2', param_config: '运输距离、能耗强度', formula: '碳排放量=运输距离（km）×能耗强度（kWh/km）×碳排放因子（kgCO2/kWh）'},
    {id: 2, method_name: '普速铁路货运碳排放量', emission_type: '能源消耗', data_type: '系统默认', is_referenced: 0, is_enabled: 1, unit: 'kgCO2', param_config: '运输距离、货物重量、能耗强度', formula: '碳排放量=运输距离（km）×货物重量（t）×能耗强度（kWh/tkm）×碳排放因子（kgCO2/kWh）'}
];
var calculationMethodsData = [];

function loadCalculationMethods() {
    fetch('/api/calculation_methods')
    .then(function(response) { return response.json(); })
    .then(function(data) {
        calculationMethodsData = data;
        renderCalculationMethods();
    })
    .catch(function() {
        calculationMethodsData = JSON.parse(JSON.stringify(defaultMethods));
        renderCalculationMethods();
    });
}

function renderCalculationMethods() {
    var container = document.getElementById('methodContent');
    if (!container) return;
    var html = '<div style="display:flex;flex-direction:column;height:100%;"><div style="display:flex;justify-content:space-between;align-items:center;padding-bottom:8px;border-bottom:1px solid #e1e8ed;flex-shrink:0;"><div style="font-size:15px;font-weight:bold;">核算方法配置</div><div style="display:flex;gap:6px;"><button class="btn btn-primary" onclick="openMethodModal()" style="font-size:13px;padding:6px 16px;">➕ 新增</button><button class="btn" onclick="openMethodModal(\'edit\')" style="font-size:13px;padding:6px 16px;">✏️ 编辑</button><button class="btn btn-danger" onclick="deleteMethod()" style="font-size:13px;padding:6px 16px;">🗑️ 删除</button></div></div><div style="flex:1;overflow:auto;margin-top:6px;"><table style="width:100%;border-collapse:collapse;font-size:13px;"><thead><tr style="background:#f8f9fa;border-bottom:2px solid #e1e8ed;"><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:40px;">序号</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;">方法名称</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:80px;">排放类型</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:80px;">数据类型</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:60px;">引用</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:60px;">启用</th><th style="padding:8px 12px;text-align:center;border:1px solid #e1e8ed;width:80px;">操作</th></tr></thead><tbody>';
    for (var i = 0; i < calculationMethodsData.length; i++) {
        var m = calculationMethodsData[i];
        html += '<tr style="background:' + (i % 2 === 0 ? 'white' : '#fafbfc') + ';"><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + (i+1) + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + m.method_name + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + m.emission_type + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + m.data_type + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + (m.is_referenced ? '是' : '否') + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;">' + (m.is_enabled ? '是' : '否') + '</td><td style="padding:6px 10px;text-align:center;border:1px solid #e1e8ed;"><span style="color:#3498db;cursor:pointer;font-size:13px;" onclick="viewMethodDetail(' + i + ')">📋 详情</span></td></tr>';
    }
    html += '</tbody></table></div></div>';
    container.innerHTML = html;
}

function viewMethodDetail(index) {
    var m = calculationMethodsData[index];
    if (!m) return;
    alert('📋 方法详情\n\n名称：' + m.method_name + '\n排放类型：' + m.emission_type + '\n数据类型：' + m.data_type + '\n单位：' + (m.unit || 'kgCO2') + '\n参数：' + m.param_config + '\n公式：' + m.formula);
}

function openMethodModal(action) {
    var modal = document.getElementById('methodModal');
    var title = document.getElementById('methodModalTitle');
    if (action === 'edit') {
        if (calculationMethodsData.length === 0) { alert('请先添加核算方法'); return; }
        var idx = prompt('请输入要编辑的序号（1-' + calculationMethodsData.length + '）：');
        if (!idx) return;
        idx = parseInt(idx) - 1;
        if (idx < 0 || idx >= calculationMethodsData.length) { alert('序号无效'); return; }
        var m = calculationMethodsData[idx];
        title.textContent = '编辑核算方法';
        document.getElementById('methodEditIndex').value = idx;
        document.getElementById('methodName').value = m.method_name;
        document.getElementById('methodEmissionType').value = m.emission_type;
        document.getElementById('methodDataType').value = m.data_type;
        document.getElementById('methodUnit').value = m.unit || 'kgCO2';
        document.getElementById('methodParams').value = m.param_config || '';
        document.getElementById('methodFormula').value = m.formula || '';
        document.getElementById('methodReferenced').value = m.is_referenced || 0;
        document.getElementById('methodEnabled').value = m.is_enabled || 1;
    } else {
        title.textContent = '新增核算方法';
        document.getElementById('methodEditIndex').value = '';
        document.getElementById('methodName').value = '';
        document.getElementById('methodEmissionType').value = '能源消耗';
        document.getElementById('methodDataType').value = '系统默认';
        document.getElementById('methodUnit').value = 'kgCO2';
        document.getElementById('methodParams').value = '运输距离、货物重量、碳排放因子';
        document.getElementById('methodFormula').value = '碳排放量=运输距离（km）×货物重量（t）×能耗强度（kWh/tkm）×碳排放因子（kgCO2/kWh）';
        document.getElementById('methodReferenced').value = 0;
        document.getElementById('methodEnabled').value = 1;
    }
    modal.style.display = 'flex';
}

function closeMethodModal() {
    document.getElementById('methodModal').style.display = 'none';
}

function saveMethod() {
    var name = document.getElementById('methodName').value.trim();
    var emissionType = document.getElementById('methodEmissionType').value;
    var dataType = document.getElementById('methodDataType').value;
    var unit = document.getElementById('methodUnit').value.trim();
    var params = document.getElementById('methodParams').value.trim();
    var formula = document.getElementById('methodFormula').value.trim();
    var referenced = parseInt(document.getElementById('methodReferenced').value);
    var enabled = parseInt(document.getElementById('methodEnabled').value);
    var editIndex = document.getElementById('methodEditIndex').value;
    if (!name) { alert('请输入计算方法名称'); return; }
    if (!unit) { alert('请输入单位'); return; }
    var methodData = { method_name: name, emission_type: emissionType, data_type: dataType, unit: unit, param_config: params, formula: formula, is_referenced: referenced, is_enabled: enabled };
    if (editIndex !== '') {
        var idx = parseInt(editIndex);
        calculationMethodsData[idx] = { ...calculationMethodsData[idx], ...methodData };
        alert('✅ 核算方法已更新');
    } else {
        methodData.id = calculationMethodsData.length + 1;
        calculationMethodsData.push(methodData);
        alert('✅ 核算方法已添加');
    }
    closeMethodModal();
    renderCalculationMethods();
}

function deleteMethod() {
    if (calculationMethodsData.length === 0) { alert('没有可删除的核算方法'); return; }
    var idx = prompt('请输入要删除的序号（1-' + calculationMethodsData.length + '）：');
    if (!idx) return;
    idx = parseInt(idx) - 1;
    if (idx < 0 || idx >= calculationMethodsData.length) { alert('序号无效'); return; }
    if (confirm('确定要删除 "' + calculationMethodsData[idx].method_name + '" 吗？')) {
        calculationMethodsData.splice(idx, 1);
        renderCalculationMethods();
        alert('✅ 核算方法已删除');
    }
}


// ============================================================
// 窗口自适应 & 模态框关闭
// ============================================================

window.addEventListener('resize', function() {});

document.addEventListener('click', function(e) {
    var modal = document.getElementById('methodModal');
    if (modal && modal.style.display === 'flex') {
        if (e.target.classList.contains('modal-overlay')) {
            closeMethodModal();
        }
    }
});
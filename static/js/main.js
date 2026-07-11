// static/js/main.js - 完整菜单配置

var menuData = [
    { name: '🏠 首页', url: '/' },
    {
        name: '📊 碳核算管理',
        children: [
            { name: '排放源配置', url: '/emission_source' },
            { name: '排放因子配置', url: '/emission_factor' },
            { name: '运营组织碳核算', url: '/organization' },
            { name: '运输链碳核算', url: '/transport_chain' },
            { name: '产品碳足迹核算', url: '/product_footprint' }
        ]
    },
    {
        name: '🌿 碳减排管理',
        children: [
            { name: '碳减排概览', url: '/reduction_overview' },
            { name: '碳减排目标', url: '/reduction_target' },
            { name: '碳排放预测', url: '/reduction_forecast' },
            { name: '碳减排措施', url: '/reduction_measure' }
        ]
    },
    {
        name: '💰 碳金融管理',
        children: [
            { name: '资产开发管理', url: '/carbon_finance/asset_development' }
        ]
    },
    {
        name: '⚙️ 系统管理',
        children: [
            { name: '用户管理', url: '/settings' }
        ]
    }
];

// ===== 渲染菜单 =====
function renderMenu() {
    var container = document.getElementById('navMenu');
    if (!container) return;
    container.innerHTML = '';
    var currentPath = window.location.pathname;
    menuData.forEach(function(item) {
        var wrapper = document.createElement('div');
        wrapper.className = 'menu-item';
        var btn = document.createElement('button');
        btn.className = 'menu-btn';
        var isActive = false;
        if (item.url && currentPath === item.url) isActive = true;
        if (item.children) {
            item.children.forEach(function(child) {
                if (currentPath === child.url) isActive = true;
            });
        }
        if (isActive) btn.classList.add('active');
        var label = document.createElement('span');
        label.textContent = item.name;
        btn.appendChild(label);
        if (item.children) {
            var arrow = document.createElement('span');
            arrow.className = 'arrow' + (isActive ? ' open' : '');
            arrow.textContent = '▼';
            btn.appendChild(arrow);
            btn.onclick = function(e) {
                e.stopPropagation();
                var submenu = this.parentElement.querySelector('.submenu');
                var arrowEl = this.querySelector('.arrow');
                if (submenu) {
                    submenu.classList.toggle('open');
                    if (arrowEl) arrowEl.classList.toggle('open');
                }
            };
            var submenu = document.createElement('div');
            submenu.className = 'submenu' + (isActive ? ' open' : '');
            item.children.forEach(function(child) {
                var subBtn = document.createElement('button');
                subBtn.className = 'sub-btn';
                if (currentPath === child.url) subBtn.classList.add('active');
                subBtn.textContent = child.name;
                subBtn.onclick = function(e) {
                    e.stopPropagation();
                    window.location.href = child.url;
                };
                submenu.appendChild(subBtn);
            });
            wrapper.appendChild(btn);
            wrapper.appendChild(submenu);
        } else {
            btn.onclick = function() { window.location.href = item.url; };
            wrapper.appendChild(btn);
        }
        container.appendChild(wrapper);
    });
}

// ===== 页面加载完成后渲染菜单 =====
document.addEventListener('DOMContentLoaded', function() {
    renderMenu();
});
/**
 * 运输链碳核算 - 前端交互逻辑
 */

class TransportChain {
    constructor() {
        this.currentMode = 'passenger';
        this.init();
    }

    init() {
        // 模式切换
        document.querySelectorAll('.mode-tab').forEach(tab => {
            tab.addEventListener('click', () => this.switchMode(tab));
        });

        // 查询按钮
        document.getElementById('calculateBtn').addEventListener('click', () => this.calculate());

        // 重置按钮
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());

        // 智能推荐
        document.getElementById('suggestBtn').addEventListener('click', () => this.getSuggestion());

        // 历史记录
        document.getElementById('historyBtn').addEventListener('click', () => this.showHistory());
        document.getElementById('closeHistory').addEventListener('click', () => this.hideHistory());
        document.getElementById('refreshHistory').addEventListener('click', () => this.loadHistory());

        // 导出报告
        document.getElementById('exportBtn').addEventListener('click', () => this.exportReport());

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.hideHistory();
            if (e.key === 'Enter') this.calculate();
        });

        // 初始加载默认计算
        this.calculate();

        // 加载历史
        this.loadHistory();

        // 点击模态框外部关闭
        document.querySelector('.modal').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) this.hideHistory();
        });
    }

    switchMode(tab) {
        // 更新tab状态
        document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // 切换表单
        this.currentMode = tab.dataset.mode;
        document.querySelectorAll('.query-form').forEach(f => f.classList.remove('active'));

        if (this.currentMode === 'passenger') {
            document.querySelector('.passenger-form').classList.add('active');
        } else {
            document.querySelector('.freight-form').classList.add('active');
        }

        // 更新标签
        this.updateLabels();

        // 自动计算
        this.calculate();
    }

    updateLabels() {
        const isPassenger = this.currentMode === 'passenger';

        // 更新卡片标签
        document.querySelectorAll('.compare-card .data-row .label').forEach(el => {
            if (el.textContent.includes('载客量') || el.textContent.includes('重量')) {
                el.textContent = isPassenger ? '载客量' : '货物重量';
            }
        });

        // 更新强度单位
        const unit = isPassenger ? 'g CO₂/人km' : 'g CO₂/吨km';
        document.querySelectorAll('.metric-value .unit').forEach(el => {
            if (el.textContent.includes('g CO₂')) {
                // 只更新强度相关的单位
            }
        });
    }

    getParams() {
        if (this.currentMode === 'passenger') {
            return {
                transport_type: 'passenger',
                mode: document.getElementById('passengerMode').value,
                passengers: parseInt(document.getElementById('passengerCount').value) || 150,
                distance: parseFloat(document.getElementById('passengerDistance').value) || 1200,
                seat_type: document.getElementById('seatType').value,
                origin: document.getElementById('origin').value || '北京',
                destination: document.getElementById('destination').value || '上海'
            };
        } else {
            return {
                transport_type: 'freight',
                mode: document.getElementById('freightMode').value,
                weight: parseFloat(document.getElementById('freightWeight').value) || 1000,
                distance: parseFloat(document.getElementById('freightDistance').value) || 1000,
                container: document.getElementById('containerType').value === '1',
                origin: document.getElementById('freightOrigin').value || '长沙北',
                destination: document.getElementById('freightDest').value || '广州'
            };
        }
    }

    async calculate() {
        const params = this.getParams();

        // 显示加载状态
        this.showLoading();

        try {
            // 先获取对比数据
            const compareResponse = await fetch('/transport/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });

            const compareResult = await compareResponse.json();

            if (compareResult.status === 'success') {
                this.updateUI(compareResult.data, params);
            }

            // 也获取单一计算结果用于保存
            const calcResponse = await fetch('/transport/calculate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(params)
            });

            const calcResult = await calcResponse.json();

        } catch (error) {
            console.error('计算失败:', error);
            this.showError('计算失败，请检查网络连接');
        }
    }

    updateUI(data, params) {
        const isPassenger = this.currentMode === 'passenger';
        const modeKeys = isPassenger
            ? ['rail_highspeed', 'road_bus', 'air']
            : ['rail', 'road', 'air'];

        // 更新指标
        const mainMode = isPassenger ? 'rail_highspeed' : 'rail';
        const mainData = data[mainMode] || data[modeKeys[0]] || {};
        const roadData = data[isPassenger ? 'road_bus' : 'road'] || {};
        const airData = data['air'] || {};

        // 总里程
        const distance = mainData.distance || params.distance || 0;
        document.getElementById('totalDistance').innerHTML =
            `${distance.toLocaleString()} <span class="unit">km</span>`;

        // 总碳排放
        const emission = mainData.total_emission || 0;
        document.getElementById('totalEmission').innerHTML =
            `${emission.toFixed(1)} <span class="unit">t CO₂e</span>`;

        // 碳排放强度
        const intensity = mainData.intensity || 0;
        const unit = isPassenger ? 'g CO₂/人km' : 'g CO₂/吨km';
        document.getElementById('avgIntensity').innerHTML =
            `${intensity.toFixed(1)} <span class="unit">${unit}</span>`;

        // 节碳量
        const savings = data.savings || {};
        const saved = savings.vs_road || 0;
        document.getElementById('totalSaved').innerHTML =
            `${saved.toFixed(1)} <span class="unit">t CO₂e</span>`;

        // 更新铁路卡片
        this.updateCard('rail', mainData, params, isPassenger);

        // 更新公路卡片
        this.updateCard('road', roadData, params, isPassenger);

        // 更新航空卡片
        this.updateCard('air', airData, params, isPassenger);

        // 更新对比摘要
        document.getElementById('vsRailRoad').textContent =
            `${savings.vs_road ? '-' + savings.vs_road.toFixed(1) : '0'} t CO₂e`;
        document.getElementById('saveRate').textContent =
            `${savings.saving_rate ? savings.saving_rate.toFixed(1) : '0'}%`;

        // 铁路 vs 航空
        const airEmission = airData.total_emission || 0;
        const railEmission = mainData.total_emission || 0;
        const vsAir = airEmission - railEmission;
        document.getElementById('vsRailAir').textContent =
            `${vsAir > 0 ? '-' : ''}${Math.abs(vsAir).toFixed(1)} t CO₂e`;

        // 更新进度条
        const maxEmission = Math.max(
            mainData.total_emission || 0,
            roadData.total_emission || 0,
            airData.total_emission || 0,
            1
        );

        const railPercent = ((mainData.total_emission || 0) / maxEmission * 100);
        const roadPercent = ((roadData.total_emission || 0) / maxEmission * 100);
        const airPercent = ((airData.total_emission || 0) / maxEmission * 100);

        document.getElementById('barRail').style.width = `${Math.min(railPercent, 100)}%`;
        document.getElementById('barRoad').style.width = `${Math.min(roadPercent, 100)}%`;
        document.getElementById('barAir').style.width = `${Math.min(airPercent, 100)}%`;

        document.getElementById('barRailVal').textContent =
            `${(mainData.total_emission || 0).toFixed(1)} t`;
        document.getElementById('barRoadVal').textContent =
            `${(roadData.total_emission || 0).toFixed(1)} t`;
        document.getElementById('barAirVal').textContent =
            `${(airData.total_emission || 0).toFixed(1)} t`;
    }

    updateCard(type, data, params, isPassenger) {
        const prefix = type === 'rail' ? 'rail' :
                      type === 'road' ? 'road' : 'air';

        const distanceEl = document.getElementById(`${prefix}Distance`);
        const emissionEl = document.getElementById(`${prefix}Emission`);
        const intensityEl = document.getElementById(`${prefix}Intensity`);
        const capacityEl = document.getElementById(`${prefix}Capacity`);

        if (distanceEl) {
            distanceEl.textContent = `${(data.distance || params.distance || 0).toLocaleString()} km`;
        }

        if (emissionEl) {
            emissionEl.textContent = `${(data.total_emission || 0).toFixed(1)} t CO₂e`;
        }

        if (intensityEl) {
            const unit = isPassenger ? 'g CO₂/人km' : 'g CO₂/吨km';
            intensityEl.textContent = `${(data.intensity || 0).toFixed(1)} ${unit}`;
        }

        if (capacityEl) {
            if (isPassenger) {
                capacityEl.textContent = `${data.passengers || params.passengers || 0} 人`;
            } else {
                capacityEl.textContent = `${data.weight || params.weight || 0} 吨`;
            }
        }
    }

    async getSuggestion() {
        const params = this.getParams();

        try {
            const response = await fetch('/transport/route-suggestion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    origin: params.origin || '北京',
                    destination: params.destination || '上海',
                    transport_type: this.currentMode
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                const data = result.data;
                alert(`💡 智能推荐\n\n` +
                      `路线: ${data.origin} → ${data.destination}\n` +
                      `距离: ${data.distance} km\n` +
                      `推荐方式: ${data.emoji} ${data.mode_name}\n` +
                      `理由: ${data.reason}`);
            }
        } catch (error) {
            console.error('获取推荐失败:', error);
            this.showError('获取推荐失败，请稍后重试');
        }
    }

    async showHistory() {
        document.getElementById('historyModal').classList.add('show');
        await this.loadHistory();
    }

    hideHistory() {
        document.getElementById('historyModal').classList.remove('show');
    }

    async loadHistory() {
        const filter = document.getElementById('historyFilter').value;
        const listEl = document.getElementById('historyList');

        listEl.innerHTML = '<div class="loading">加载中...</div>';

        try {
            const url = `/transport/history?type=${filter === 'all' ? '' : filter}`;
            const response = await fetch(url);
            const result = await response.json();

            if (result.status === 'success' && result.data.length > 0) {
                listEl.innerHTML = result.data.map(item => `
                    <div class="history-item">
                        <div class="info">
                            <span class="type">${item.transport_type === 'passenger' ? '🚆 客运' : '🚛 货运'}</span>
                            <span class="detail">${item.mode} · ${item.distance} km · ${item.passengers || item.weight} ${item.transport_type === 'passenger' ? '人' : '吨'}</span>
                            <span class="detail">${new Date(item.created_at).toLocaleString()}</span>
                        </div>
                        <div class="emission">${item.total_emission.toFixed(1)} t CO₂e</div>
                    </div>
                `).join('');
            } else {
                listEl.innerHTML = '<div class="loading">暂无历史记录</div>';
            }
        } catch (error) {
            listEl.innerHTML = '<div class="loading">加载失败，请重试</div>';
        }
    }

    reset() {
        if (this.currentMode === 'passenger') {
            document.getElementById('passengerCount').value = 150;
            document.getElementById('passengerDistance').value = 1200;
            document.getElementById('passengerMode').value = 'rail_highspeed';
            document.getElementById('seatType').value = 'economy';
            document.getElementById('origin').value = '北京';
            document.getElementById('destination').value = '上海';
        } else {
            document.getElementById('freightWeight').value = 1000;
            document.getElementById('freightDistance').value = 1000;
            document.getElementById('freightMode').value = 'rail';
            document.getElementById('containerType').value = '0';
            document.getElementById('freightOrigin').value = '长沙北';
            document.getElementById('freightDest').value = '广州';
        }

        this.calculate();
    }

    exportReport() {
        const params = this.getParams();
        const isPassenger = this.currentMode === 'passenger';

        // 收集数据
        const railEmission = document.getElementById('railEmission').textContent;
        const roadEmission = document.getElementById('roadEmission').textContent;
        const airEmission = document.getElementById('airEmission').textContent;
        const savingRate = document.getElementById('saveRate').textContent;

        const report = `
=== 运输链碳核算报告 ===
生成时间: ${new Date().toLocaleString()}
运输类型: ${isPassenger ? '客运' : '货运'}

--- 参数设置 ---
${isPassenger ?
    `方式: ${document.getElementById('passengerMode').selectedOptions[0].text}
座位: ${document.getElementById('seatType').selectedOptions[0].text}
人数: ${document.getElementById('passengerCount').value}
距离: ${document.getElementById('passengerDistance').value} km` :
    `方式: ${document.getElementById('freightMode').selectedOptions[0].text}
重量: ${document.getElementById('freightWeight').value} 吨
距离: ${document.getElementById('freightDistance').value} km
集装箱: ${document.getElementById('containerType').value === '1' ? '是' : '否'}`
}

--- 碳排放对比 ---
铁路: ${railEmission}
公路: ${roadEmission}
航空: ${airEmission}

--- 节碳效益 ---
节碳量: ${document.getElementById('vsRailRoad').textContent}
节碳率: ${savingRate}
        `;

        // 下载报告
        const blob = new Blob([report], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `碳核算报告_${new Date().toISOString().slice(0,10)}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }

    showLoading() {
        // 简单加载指示
        const btn = document.getElementById('calculateBtn');
        const originalText = btn.innerHTML;
        btn.innerHTML = '⏳ 计算中...';
        btn.disabled = true;

        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 600);
    }

    showError(message) {
        // 简单错误提示
        alert('❌ ' + message);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    window.transportChain = new TransportChain();
});
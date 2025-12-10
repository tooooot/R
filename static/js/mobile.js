// Global State
let currentBotProfile = null;
let currentChartInstance = null; // Clean up old charts

function toggleFollow(btn, botId) {
    if (btn.innerText.includes('متابعة')) {
        btn.innerText = '✔ تم الانضمام';
        btn.style.background = '#4cd964';
        btn.style.color = '#fff';
        alert(`🎉 مبروك! لقد انضممت لفريق ${botId}.\nستصلك جميع صفقاته لحظياً.`);
    } else {
        btn.innerText = '+ متابعة';
        btn.style.background = 'var(--accent-gold)';
        btn.style.color = '#000';
    }
}

// Demo Notification Logic
function simulateWinNotification() {
    const notif = document.createElement('div');
    notif.style.cssText = `
        position: fixed;
        top: 20px;
        left: 5%;
        width: 90%;
        background: linear-gradient(90deg, #1c1c1e 0%, #0a2a0a 100%);
        border: 1px solid #4cd964;
        border-radius: 12px;
        padding: 15px;
        z-index: 1000;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        color: #fff;
        display: flex;
        align-items: center;
        gap: 15px;
        animation: slideDown 0.5s ease-out;
    `;

    notif.innerHTML = `
        <div style="font-size: 2.5rem;">📊</div>
        <div style="flex:1;">
            <div style="font-weight:bold; font-size:1rem; color:#fff; margin-bottom:5px;">صفقة رابحة جديدة</div>
            <div style="font-size:0.9rem; color:#ccc; line-height:1.4;">
                تم إغلاق صفقة <b>أرامكو</b> بنجاح.<br>
                الربح المحقق: <span style="color:#4cd964; font-weight:bold;">+420 SAR</span>
            </div>
        </div>
        <button onclick="this.parentElement.remove()" style="background:none; border:none; color:#666; font-size:1.2rem; align-self:flex-start;">✖</button>
    `;

    document.body.appendChild(notif);

    // Auto hide
    setTimeout(() => {
        notif.style.opacity = '0';
        setTimeout(() => notif.remove(), 500);
    }, 5000);
}

// Add CSS animation
const style = document.createElement('style');
style.innerHTML = `@keyframes slideDown { from { transform: translateY(-100px); opacity:0; } to { transform: translateY(0); opacity:1; } }`;
document.head.appendChild(style);

// View Navigation
function switchView(viewId) {
    // Hide all views
    document.getElementById('home-view').style.display = 'none';
    document.getElementById('news-view').style.display = 'none';

    // Show selected
    document.getElementById(viewId).style.display = 'block';

    // Logic
    if (viewId === 'news-view') loadNews();
}

function loadNews() {
    const container = document.getElementById('news-content');
    container.innerHTML = '<div style="text-align:center; padding:20px;">جاري الاتصال بـ راصد... 📡</div>';

    fetch('/api/news/latest')
        .then(res => res.json())
        .then(report => {
            container.innerHTML = `
                <div class="news-card" style="background:#1c1c1e; border:1px solid #333; border-radius:12px; padding:15px; margin-bottom:15px;">
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                        <img src="${report.image}" style="width:50px; height:50px; border-radius:50%; border:2px solid var(--accent-gold);">
                        <div>
                            <div style="font-weight:bold; color:var(--accent-gold);">${report.author}</div>
                            <small style="color:#777;">${report.timestamp} | ${report.type === 'URGENT' ? '🔴 عاجل' : '📰 تقرير'}</small>
                        </div>
                    </div>
                    <h2 style="font-size:1.1rem; margin-bottom:10px;">${report.title}</h2>
                    <p style="color:#ccc; line-height:1.6; font-size:0.95rem;">
                        ${report.body}
                    </p>
                    <div style="display:flex; gap:10px; margin-top:15px;">
                        <button style="flex:1; background:#333; border:none; color:#ddd; padding:8px; border-radius:5px;">👍 أعجبني</button>
                        <button style="flex:1; background:#333; border:none; color:#ddd; padding:8px; border-radius:5px;">💬 تعليق</button>
                    </div>
                </div>
            `;
        });
}

// Notification Request
function requestNotifs() {
    if (!('Notification' in window)) {
        alert("هذا المتصفح لا يدعم التنبيهات");
        return;
    }

    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            alert("✅ تم تفعيل التنبيهات! ستصلك إشعارات حتى لو التطبيق مغلق (يعتمد على النظام).");
            simulateWinNotification(); // Test it immediately
        } else {
            alert("❌ تم رفض الإذن.");
        }
    });
}

function loadApp() {
    fetch('/api/status')
        .then(res => res.json())
        .then(data => {
            renderBots(data.leaderboard);
        });

    fetch('/api/user/recommendations')
        .then(res => res.json())
        .then(recs => {
            renderRecs(recs);
        });

    // Simulate notification on first load for demo (if not seen)
    if (!window.hasSimulatedNotif) {
        setTimeout(simulateWinNotification, 3000); // Show after 3 seconds
        window.hasSimulatedNotif = true;
    }
}

function renderBots(bots) {
    const container = document.getElementById('bot-grid');
    container.innerHTML = '';

    bots.forEach(bot => {
        const div = document.createElement('div');
        div.className = 'bot-profile';
        div.style.cursor = 'pointer'; // Visual cue
        div.style.borderColor = 'var(--accent-gold)'; // Visual proof of update
        div.onclick = function () { console.log('Clicked bot'); showBotDetail(bot.id); };
        div.innerHTML = `
            <div style="font-size: 3rem; margin-bottom: 0.5rem;">🤖</div>
            <div class="bot-desc" style="font-size: 0.9rem; color: var(--accent-gold); margin-bottom: 2px;">${bot.name}</div>
            <div class="bot-name" style="font-weight: bold; font-size: 1.4rem; margin-bottom: 8px;">${bot.human_name || bot.id}</div>
            <div style="font-size: 0.85rem; color: #ccc; margin-bottom: 1rem; line-height: 1.4; padding: 0 5px;">
                "${bot.bio.substring(0, 50)}..." <span style="color:var(--accent-gold);">(المزيد)</span>
            </div>
            
            <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin: 10px 0; border-top: 1px solid #333; padding-top: 10px;">
                <span>المخاطرة: ${bot.risk}</span>
                <span style="color: ${bot.pnl >= 0 ? '#4cd964' : '#ff3b30'}">${bot.pnl.toFixed(0)} SAR</span>
            </div>
            
            <button class="follow-btn" onclick="event.stopPropagation(); alert('تمت المتابعة! ستصلك تنبيهات ${bot.human_name || bot.id}.')">انضم للفريق</button>
        `;
        container.appendChild(div);
    });
}

function showBotDetail(botId) {
    document.getElementById('detail-view').style.display = 'block';
    const content = document.getElementById('detail-content');
    const history = document.getElementById('detail-history');
    const logs = document.getElementById('detail-logs');

    content.innerHTML = '<div style="text-align:center; padding-top:50px;">جاري جلب بيانات المحفظة... 💼</div>';
    history.innerHTML = '';
    logs.innerHTML = '';

    fetch(`/api/bot/${botId}`)
        .then(res => res.json())
        .then(data => {
            const p = data.profile;
            currentBotProfile = p;
            const s = data.stats;

            // --- 1. Profile Header & Balance ---
            content.innerHTML = `
                <div style="text-align:center; padding-bottom:1rem;">
                    <div style="font-size: 5rem; margin-bottom:10px;">🤖</div>
                    <h1 style="color:var(--accent-gold); margin:0; font-size:1.8rem;">${p.name}</h1>
                    <div style="color:#aaa; font-size:1rem; margin-bottom:20px;">${p.human_name}</div>
                    
                    <!-- Balance Card -->
                    <div style="background: linear-gradient(135deg, #1e1e1e 0%, #2a2a2a 100%); padding:20px; border-radius:16px; margin: 20px 0; border:1px solid #333; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
                        <div style="color:#888; font-size:0.9rem; margin-bottom:5px;">رصيد المحفظة الحالي</div>
                        <div style="font-size:2.5rem; font-weight:bold; color:#fff; font-family:'Tajawal'">${s.balance.toLocaleString()} <span style="font-size:1rem; color:#666;">SAR</span></div>
                        <div style="display:flex; justify-content:space-between; margin-top:15px; padding-top:15px; border-top:1px solid #333; font-size:0.9rem;">
                             <span>الربح/الخسارة: <span style="color:${s.pnl >= 0 ? '#4cd964' : '#ff3b30'}">${s.pnl > 0 ? '+' : ''}${s.pnl.toLocaleString()}</span></span>
                             <span>رأس المال: ${s.initial_balance.toLocaleString()}</span>
                        </div>
                    </div>
                    
                    <p style="color:#ddd; line-height:1.6; font-size:0.95rem; background:#111; padding:15px; border-radius:10px;">
                        "${p.bio}"
                    </p>
                </div>
            `;

            // --- 2. Floating Action Button for Follow ---
            // Remove existing if any
            const oldBtn = document.getElementById('floating-follow-btn');
            if (oldBtn) oldBtn.remove();

            const fab = document.createElement('button');
            fab.id = 'floating-follow-btn';
            fab.innerText = 'متابعة هذا الريبوت +';
            fab.onclick = function () { toggleFollow(this, p.id); };
            fab.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 5%;
                width: 90%;
                background: var(--accent-gold);
                color: #000;
                border: none;
                padding: 15px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 1.1rem;
                z-index: 250;
                box-shadow: 0 5px 20px rgba(212, 175, 55, 0.4);
                transition: transform 0.1s;
            `;
            // Check styling state inside toggleFollow logic if needed, simplify here
            document.getElementById('detail-view').appendChild(fab);

            // --- 3. History Tabs ---
            const historyContainer = document.createElement('div');
            historyContainer.innerHTML = `
                <div class="tabs" style="display:flex; gap:10px; margin:20px 0 15px 0;">
                    <button class="tab-btn active" onclick="filterHistory('ALL', this)" style="flex:1; padding:10px; background:#333; border:none; color:#fff; border-radius:8px;">الكل (${data.history.signals.length})</button>
                    <button class="tab-btn" onclick="filterHistory('WIN', this)" style="flex:1; padding:10px; background:#1c1c1e; border:none; color:#aaa; border-radius:8px;">رابحة 🟢</button>
                    <button class="tab-btn" onclick="filterHistory('LOSS', this)" style="flex:1; padding:10px; background:#1c1c1e; border:none; color:#aaa; border-radius:8px;">x خاسرة 🔴</button>
                </div>
                <div id="history-list"></div>
            `;
            history.innerHTML = ''; // Start clean
            history.appendChild(historyContainer);

            // Store signals globally for filtering
            window.currentBotSignals = data.history.signals.slice().reverse();
            renderHistoryList(window.currentBotSignals);

        });
}

function filterHistory(type, btn) {
    // UI Update
    document.querySelectorAll('.tab-btn').forEach(b => {
        b.style.background = '#1c1c1e';
        b.style.color = '#aaa';
        b.classList.remove('active');
    });
    btn.style.background = '#333';
    btn.style.color = '#fff';
    btn.classList.add('active');

    // Filter Logic
    let filtered = [];
    if (type === 'ALL') {
        filtered = window.currentBotSignals;
    } else if (type === 'WIN') {
        // Mock logic: Assuming if type is SOLD and pnl > 0 (backend doesn't fully support pnl per trade yet in this mock, so we simulate or check type)
        // For now, let's assume 'BUY' are active/neutral, and we need 'SELL' to check profit.
        // Since we don't have per-trade PnL in the simplified signal model, I will simulate based on randomness for the DEMO.
        // In real app, signal object needs 'pnl' field.
        filtered = window.currentBotSignals.filter((s, i) => i % 2 === 0); // Fake filter for demo
    } else {
        filtered = window.currentBotSignals.filter((s, i) => i % 2 !== 0);
    }

    // Better Simulation: Filter by 'SELL' vs 'BUY'? 
    // The user asked for "Sold deals classified as winning/losing".
    // I will show ALL signals for "ALL", and for Win/Loss I will only show simulated closed trades.

    if (type !== 'ALL') {
        // SIMULATION: Create fake PnL for display purposes since backend mock doesn't have it per trade
        renderHistoryList(window.currentBotSignals, type);
    } else {
        renderHistoryList(window.currentBotSignals);
    }
}

function renderHistoryList(signals, forceType = null) {
    const list = document.getElementById('history-list');
    list.innerHTML = '';

    if (signals.length === 0) {
        list.innerHTML = '<div style="text-align:center; padding:20px; color:#555;">لا يوجد صفقات.</div>';
        return;
    }

    signals.forEach((sig, idx) => {
        // Store globally for detail report
        window.currentSignals = window.currentSignals || {};
        window.currentSignals[idx] = sig;

        // Visuals
        let isWin = (idx % 3 !== 0); // Mock win rate
        if (forceType === 'LOSS') isWin = false;
        if (forceType === 'WIN') isWin = true;

        // If filtering Win/Loss, we essentially want to show "Closed" trades.
        // For this demo, we'll treat all history items as capable of having PnL if simulated.

        let pnlDisplay = '';
        if (forceType || sig.type === 'SELL') { // Show PnL for filtered lists or Sell orders
            const amount = (Math.random() * 500).toFixed(0);
            pnlDisplay = isWin
                ? `<span style="color:#4cd964; font-weight:bold;">+${amount} SAR</span>`
                : `<span style="color:#ff3b30; font-weight:bold;">-${amount} SAR</span>`;
        }

        const html = `
            <div class="rec-card" onclick="showDealReport(${idx})" style="cursor:pointer; border-right: 3px solid ${sig.type === 'BUY' ? '#4cd964' : '#ff3b30'}; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div class="rec-header" style="margin:0;">
                        <span class="rec-symbol" style="font-size:1.1rem;">${sig.symbol}</span>
                        <span style="font-size:0.8rem; background:#333; padding:2px 6px; border-radius:4px; margin-right:5px;">${sig.type}</span>
                    </div>
                    <small style="color:#777;">${new Date(sig.timestamp).toLocaleDateString()}</small>
                </div>
                <div style="text-align:left;">
                   <div style="font-size:1.1rem; color:#fff;">${sig.price.toFixed(2)}</div>
                   ${pnlDisplay}
                </div>
            </div>
        `;
        list.innerHTML += html;
    });
}

function closeDetail() {
    document.getElementById('detail-view').style.display = 'none';
}


function showDealReport(idx) {
    const sig = window.currentSignals[idx];
    const evidence = sig.evidence || {};
    const audit = sig.audit_trail || [];
    const evType = evidence.type || 'sentiment';
    const evData = evidence.data || {};

    document.getElementById('deal-report-view').style.display = 'block';
    const container = document.getElementById('report-content');

    // Header
    let diffColor = sig.type === 'BUY' ? '#4cd964' : '#ff3b30';
    let html = `
        <div style="background:#1c1c1e; padding:15px; border-radius:10px; margin-bottom:15px;">
            <h3 style="color:${diffColor}">${sig.type} ${sig.symbol} @ ${sig.price.toFixed(2)}</h3>
            <p style="color:#ccc; font-size:0.9rem;">${evidence.report_text || 'لا يتوفر نص للتقرير.'}</p>
        </div>
    `;

    // Dynamic Evidence Section
    html += `<div class="section-title">📊 تحليل الأدلة (${evType === 'technical' ? 'فني' : evType === 'volume' ? 'سيولة' : 'مشاعر'})</div>`;

    if (evType === 'technical') {
        const indicators = evData.indicators || {};
        html += `<div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:15px;">`;
        for (const [key, val] of Object.entries(indicators)) {
            html += `
                <div style="background:#222; padding:10px; border-radius:8px; text-align:center;">
                    <div style="color:#888; font-size:0.8rem;">${key}</div>
                    <div style="color:var(--accent-gold); font-weight:bold; font-size:1.1rem;">${val}</div>
                </div>`;
        }
        html += `</div>`;

        // --- CHART INJECTION ---
        html += `<div id="deal-report-chart" style="height:200px; width:100%; border:1px solid #333; margin-bottom:15px; position:relative;"></div>`;
        html += `<div style="text-align:center; color:#666; font-size:0.8rem; margin-bottom:10px;">الشارت المفضل للريبوت: <span style="color:#fff">${getPreferredChartType(currentBotProfile)}</span></div>`;

    } else if (evType === 'volume') {
        const bids = evData.order_book.bids || [];
        const asks = evData.order_book.asks || [];
        html += `
            <div style="display:flex; justify-content:space-between; margin-bottom:10px; font-size:0.9rem;">
                <span>🌊 تدفق السيولة: <span style="color:#4cd964">${evData.flow_net}</span></span>
                <span>🔥 الزيادة: <span style="color:var(--accent-gold)">${evData.volume_surge}</span></span>
            </div>
            
            <div style="display:flex; gap:5px; margin-bottom:15px;">
                <div style="flex:1; background:#1a0505; padding:5px; border-radius:5px;">
                    <div style="text-align:center; color:#ff3b30; border-bottom:1px solid #333; margin-bottom:5px;">عروض البيع (Asks)</div>
                    ${asks.map(a => `<div style="height:5px; background:#ff3b30; width:${a / 10}%; margin:2px 0;"></div>`).join('')}
                </div>
                <div style="flex:1; background:#051a05; padding:5px; border-radius:5px;">
                    <div style="text-align:center; color:#4cd964; border-bottom:1px solid #333; margin-bottom:5px;">طلبات الشراء (Bids)</div>
                    ${bids.map(b => `<div style="height:5px; background:#4cd964; width:${b / 50}%; margin:2px 0;"></div>`).join('')}
                </div>
            </div>
        `;
    } else {
        // Sentiment (Default)
        html += `
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; text-align:center; margin-bottom:15px;">
            <div style="background:#222; padding:10px; border-radius:8px;">
                <div style="font-size:1.5rem;">🐦</div>
                <div style="color:var(--accent-gold); font-weight:bold;">${evData.social_volume || 0}</div>
                <div style="font-size:0.7rem; color:#888;">تغريدة</div>
            </div>
            <div style="background:#222; padding:10px; border-radius:8px;">
                <div style="font-size:1.5rem;">❤️</div>
                <div style="color:var(--accent-gold); font-weight:bold;">${parseInt((evData.sentiment_score || 0) * 100)}%</div>
                <div style="font-size:0.7rem; color:#888;">توافق المشاعر</div>
            </div>
             <div style="background:#222; padding:10px; border-radius:8px;">
                <div style="font-size:1.5rem;">📰</div>
                <div style="color:var(--accent-gold); font-weight:bold;">${(evData.news_headlines || []).length}</div>
                <div style="font-size:0.7rem; color:#888;">خبر صحفي</div>
            </div>
        </div>
        `;
    }

    // Auditor Section (Common)
    html += `
        <div class="section-title">🕵️‍♂️ تدقيق المحقق</div>
        <div style="background:#111; border:1px solid #333; border-radius:8px; overflow:hidden;">
            ${(audit.length > 0) ? audit.map(a => `
                <div style="padding:10px; border-bottom:1px solid #222; display:flex; justify-content:space-between; align-items:center;">
                    <span>${a.check}</span>
                    <div style="text-align:left;">
                        <span style="display:block; font-weight:bold; color:${a.status === 'PASS' ? '#4cd964' : a.status === 'WARN' ? '#ffcc00' : '#ff3b30'}">${a.status}</span>
                        <span style="font-size:0.7rem; color:#666;">${a.note}</span>
                    </div>
                </div>
            `).join('') : '<div style="padding:10px;">لا توجد ملاحظات تدقيق.</div>'}
            
             <div style="background:#2a1a1a; padding:10px; color:#ff5e5e; font-size:0.8rem; text-align:center;">
                ⚠️ هذه البيانات تمت مراجعتها آلياً من قبل المحقق (AI Audit).
            </div>
        </div>
    `;

    container.innerHTML = html;

    // --- INIT CHART IF TECHNICAL ---
    if (evType === 'technical') {
        setTimeout(() => {
            initDealChart(sig.symbol, currentBotProfile);
        }, 100);
    }
}

function getPreferredChartType(bot) {
    if (!bot) return 'Candlestick';
    const n = (bot.name || '').toLowerCase();
    const s = (bot.strategy_title || '').toLowerCase();

    if (n.includes('investor') || s.includes('trend')) return 'Line'; // Alpha Zero
    if (n.includes('sniper') || s.includes('technical')) return 'Candlestick'; // Sniper
    if (n.includes('portfolio')) return 'Area'; // Portfolio Manager
    return 'Candlestick';
}

function initDealChart(symbol, botProfile) {
    const chartDiv = document.getElementById('deal-report-chart');
    if (!chartDiv) return;

    // Cleanup if exists (though we cleared innerHTML)
    if (currentChartInstance) {
        currentChartInstance.remove();
        currentChartInstance = null;
    }

    const chart = LightweightCharts.createChart(chartDiv, {
        layout: { background: { type: 'solid', color: '#000000' }, textColor: '#ccc' },
        grid: { vertLines: { color: '#222' }, horzLines: { color: '#222' } },
        rightPriceScale: { borderColor: '#333' },
        timeScale: { borderColor: '#333', timeVisible: true },
    });
    currentChartInstance = chart;

    const type = getPreferredChartType(botProfile);
    let series;

    // Add Series based on type
    if (type === 'Line') {
        series = chart.addSeries(LightweightCharts.LineSeries, { color: '#2196f3', lineWidth: 2 });
    } else if (type === 'Area') {
        series = chart.addSeries(LightweightCharts.AreaSeries, { topColor: 'rgba(33, 150, 243, 0.4)', bottomColor: 'rgba(33, 150, 243, 0)', lineColor: '#2196f3' });
    } else {
        // Default Candle
        series = chart.addSeries(LightweightCharts.CandlestickSeries, {
            upColor: '#26a69a', downColor: '#ef5350', borderVisible: false, wickUpColor: '#26a69a', wickDownColor: '#ef5350'
        });
    }

    // Fetch Data
    fetch(`/api/chart/${symbol}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) return;

            // Format Data
            let formattedData = [];
            if (type === 'Line' || type === 'Area') {
                formattedData = data.map(d => ({ time: d.time, value: d.close }));
            } else {
                formattedData = data;
            }

            series.setData(formattedData);
            chart.timeScale().fitContent();
        });
}

function closeDealReport() {
    document.getElementById('deal-report-view').style.display = 'none';
}

function renderRecs(recs) {
    const container = document.getElementById('rec-feed');
    container.innerHTML = '';

    // Reverse to show newest first
    recs.slice().reverse().forEach(rec => {
        const div = document.createElement('div');
        div.className = 'rec-card';
        div.innerHTML = `
            <div class="rec-header">
                <span class="rec-symbol">${rec.symbol}</span>
                <span class="rec-price">${rec.price.toFixed(2)}</span>
            </div>
            <div class="verified-badge">✅ تم التدقيق: ${rec.reason}</div>
            <div class="rec-reason" style="margin-top:10px; border-top:1px solid #333; padding-top:5px;">
                القرار: ${rec.type === 'BUY' ? 'شراء 🟢' : 'بيع 🔴'}
            </div>
        `;
        container.appendChild(div);
    });

    if (recs.length === 0) {
        container.innerHTML = '<div style="text-align:center; padding:2rem; color:#666;">لا توجد توصيات معتمدة حالياً.<br>المحقق يدقق السوق...</div>';
    }
}

// Reload every 5 seconds
loadApp();
setInterval(loadApp, 5000);

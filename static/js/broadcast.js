function updateDashboard() {
    fetch('/api/status')
        .then(response => response.json())
        .then(data => {
            updateLeaderboard(data.leaderboard);
            updateInvestigator(data.investigator_logs);
            // Simulate adding actions to feed based on logs for now
            // In a real socket setup, we'd append. Here we just show recent logs as actions.
        })
        .catch(err => console.error(err));
}

function updateLeaderboard(bots) {
    const container = document.getElementById('leaderboard');
    container.innerHTML = '<h2>🏆 الصدارة</h2>';

    bots.slice(0, 5).forEach((bot, index) => {
        const div = document.createElement('div');
        div.className = `bot-card rank-${index + 1}`;
        const pnlClass = bot.pnl >= 0 ? '' : 'negative';
        div.innerHTML = `
            <div class="bot-name">#${index + 1} ${bot.id}</div>
            <div class="bot-pnl ${pnlClass}">${bot.pnl.toFixed(2)} SAR</div>
            <small>${bot.win_rate}% Win Rate | ${bot.status}</small>
        `;
        container.appendChild(div);
    });
}

function updateInvestigator(logs) {
    const container = document.getElementById('investigator-logs');
    container.innerHTML = '<h2>🕵️ غرفة التحقيق</h2>';

    logs.forEach(log => {
        const div = document.createElement('div');
        div.className = 'inv-log';
        div.innerHTML = `
            <span class="inv-time">[${new Date(log.timestamp).toLocaleTimeString()}]</span>
            <span class="inv-verdict ${log.verdict}">${log.verdict}</span>
            <p>Bot ${log.bot_id}: ${log.message}</p>
        `;
        container.appendChild(div);
    });
}

// Add random "Action" to center screen for visual effect
function simulateAction() {
    const actions = [
        "Bot-2 اشترى الراجحي (1120)",
        "المحقق يراجع صفقة Bot-5",
        "Bot-9 جنى أرباح سابك",
        "تحذير: سيولة عالية في قطاع البنوك"
    ];
    const container = document.getElementById('action-feed');
    const msg = actions[Math.floor(Math.random() * actions.length)];

    const div = document.createElement('div');
    div.className = 'action-item';
    div.innerHTML = `<span>${msg}</span>`;
    container.prepend(div);

    if (container.children.length > 8) {
        container.lastChild.remove();
    }
}

// Init
setInterval(updateDashboard, 2000);
setInterval(simulateAction, 3000); // Visual fluff

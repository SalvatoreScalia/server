document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const user_id = localStorage.getItem('user_id');
    const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
    const competitor_id = localStorage.getItem('competitor_id') || 'Unknown Competitor';
    if (!role || role !=='master') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = '/static/login.html';
        return;
    }
    //Initialize all commponent when page is loaded
    window.addEventListener('load', () => {
        if (role === 'master') {
            document.getElementById('master-container').style.display = 'block';
            console.log(replacePlaceholders(langStrings.connectedWelcomeMessage,{user_nickname:user_nickname}));
        }
        setupEventListeners(this);
        //setInterval(() => clearBuffer(1), 15000);
    });
});

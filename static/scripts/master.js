document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
    if (!role || role !=='master') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = '/login';
        return;
    }
    //Initialize all commponent when page is loaded
    window.addEventListener('load', () => {
        if (role === 'master') {
            populatePorts()
            populateListServers(getInfoFromServers('websocket_tasks'))
            document.getElementById('master-container').style.display = 'block';
            console.log(replacePlaceholders(langStrings.connectedWelcomeMessage,{user_nickname:user_nickname}));
        }
        setupEventListeners(this);
        //setInterval(() => clearBuffer(1), 15000);
    });
});
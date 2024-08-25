document.addEventListener('DOMContentLoaded', () => {
    const role = localStorage.getItem('role');
    if (!role || role !== 'master') {
        window.location.href = '/login';
        return;
    }

    const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
    const masterContainer = document.getElementById('master-container');
    masterContainer.style.display = 'block';
    console.log(replacePlaceholders(langStrings.connectedWelcomeMessage, { user_nickname }));
    setupEventListeners();
});

const formStartWebSocketServer = document.getElementById('formStartWebSocketServer');
formStartWebSocketServer.addEventListener('submit', funcStartWebSocketServer);
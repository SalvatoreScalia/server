document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const id = localStorage.getItem('id');
    if (!role || role !=='master') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = '/static/login.html';
        return;
    }
    if (role === 'master') {
        document.getElementById('master-container').style.display = 'block';
        // Inicia la conexión de WebSockets cuando la página se carga
        window.addEventListener('load', () => {
            connectWebSockets("/game");
        });
        console.log(replacePlaceholders(langStrings.connectWelcomeMessage,));
    }

    setupEventListeners(this);
    //setInterval(() => clearBuffer(1), 15000);
});

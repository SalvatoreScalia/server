document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const id = localStorage.getItem('id');
    if (!role || role !=='player') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = 'login.html';
        return;
    }
    if (role === 'player') {
        document.getElementById('player-container').style.display = 'block';
        // Inicia la conexión de WebSockets cuando la página se carga
        window.addEventListener('load', () => {
            connectWebSockets();
        });
        console.log(`The user: ${id} is online`);
    }

    setupEventListeners(this);
    //setInterval(() => clearBuffer(0), 15000);
});

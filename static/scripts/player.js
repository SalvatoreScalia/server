document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const user_id = localStorage.getItem('user_id');
    const nick = localStorage.getItem('nick')
    const competitor_id = localStorage.getItem('competitor_id')
    if (!role || role !=='player') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = '/static/login.html';
        return;
    }
    //Initialize all commponent when page is loaded
    window.addEventListener('load', () => {
        if (role === 'player') {
            document.getElementById('player-container').style.display = 'block';
            connectWebSockets("/game");
            console.log(`The user: ${user_id} is online`);
        }
        setupEventListeners(this);
        //setInterval(() => clearBuffer(0), 15000);
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    if (!role || role !=='player') {
        window.location.href = '/login';
        return;
    }
    
    const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
    const playerContainer = document.getElementsByClassName('container');
    playerContainer.style.display = 'block';
    console.log(replacePlaceholders(langStrings.connectedWelcomeMessage, { user_nickname }));
    setupEventListeners();
});
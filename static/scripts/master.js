document.addEventListener('DOMContentLoaded', function() {
    const role = localStorage.getItem('role');
    const user_id = localStorage.getItem('user_id');
    const user_nickname = localStorage.getItem('user_nickname')
    const competitor_id = localStorage.getItem('competitor_id')
    if (!role || role !=='master') {
        // Redirige al login si no hay rol en localStorage
        window.location.href = '/static/login.html';
        return;
    }
    //Initialize all commponent when page is loaded
    window.addEventListener('load', () => {
        if (role === 'master') {
            document.getElementById('master-container').style.display = 'block';
            console.log(replacePlaceholders(langStrings.connectWelcomeMessage,user_nickname));
            //develiper logs
            console.log(`The user: ${user_id} is online`);
            console.log(`competitor: ${competitor_id}`);
        }
        setupEventListeners(this);
        //setInterval(() => clearBuffer(1), 15000);
    });
});

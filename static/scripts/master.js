
const role = localStorage.getItem('role');
if (!role || role !== 'master') {
    window.location.href = '/login';
    return;
}

const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
console.log(replacePlaceholders(langStrings.connectedWelcomeMessage, { user_nickname }));
setupEventListeners();



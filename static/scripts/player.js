
const role = localStorage.getItem('role');
if (!role || role !=='player') {
    window.location.href = '/login';
}

const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
console.log(replacePlaceholders(langStrings.connectedWelcomeMessage, { user_nickname }));
setupEventListeners();

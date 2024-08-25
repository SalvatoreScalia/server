document.addEventListener('DOMContentLoaded', () => {
    const role = localStorage.getItem('role');
    if (!role || role !== 'master') {
        window.location.href = '/login';
        return;
    }

    const user_nickname = localStorage.getItem('user_nickname') || 'Guest';
    const masterContainer = document.getElementById('container');
    masterContainer.style.display = 'block';
    console.log(replacePlaceholders(langStrings.connectedWelcomeMessage, { user_nickname }));
    setupEventListeners();
});

document.getElementById('selectPort')?.addEventListener('click', async function () {
    const selectElement = document.getElementById('selectPort');

    if (selectElement.options.length > 0) {
        return;
    }

    showLoadingScreen();
    try{
        const listAvailablePorts = await getInfoFromServer('available_ports');
        populatePorts(listAvailablePorts);
    } catch (error) {
        console.error('Error loading server information:', error);
        hideLoadingScreen();
    }finally{
        hideLoadingScreen();
    }
});

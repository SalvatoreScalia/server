function setupEventListeners() {    
    let command;

    document.getElementById('stopButton')?.addEventListener('click', function(){
        command = JSON.stringify(
            {
                command:"/stop",
                scapeSave:false
            }
        );
        WebSocketService.sendCommand(command);
    });
    document.getElementById('updateStatusButton')?.addEventListener('click', function() {
        console.log('updateButtonPress');
        command = JSON.stringify({ command: '/updateState', index: 0 });
        WebSocketService.sendCommand(command);
    });
    document.getElementById('reconnectButton')?.addEventListener('click', function() {
        let path = '/game'
        let port = ':3001'
        reconnectSocket(port,path);
    });
    document.getElementById('toggleScrollButton')?.addEventListener('click',function(){
        toggleAutoScroll(this);
    })
    document.getElementById('clearBufferButton')?.addEventListener('click', function() {
        clearBuffer(0);
    });
    document.getElementById('logoutButton')?.addEventListener('click', function() {
        localStorage.clear() //removeItem('userRole');
        window.location.href = '/login';
    });
    document.getElementById('reloadAvailableServers')?.addEventListener('click', async function() {
        showLoadingScreen();
        try {
            const serversInfo = await getInfoFromServer('websocket_server_tasks');
            populateListServers(serversInfo);
        } catch (error) {
            console.error('Error loading server information:', error);
            hideLoadingScreen();
        }finally{
            hideLoadingScreen();
        }
    });
}

document.getElementById('formStartWebSocketServer')?.addEventListener('submit', funcStartWebSocketServer);
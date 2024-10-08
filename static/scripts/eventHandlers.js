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
        let port = localStorage.getItem('wss_port');
        let path = localStorage.getItem('wss_path') || '';
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
            const dictServersInfo = await getInfoFromServer('websocket_server_tasks');
    
            if (!dictServersInfo || Object.keys(dictServersInfo).length === 0) {
                console.log('It appears that there are no servers online at the moment.');
                // some alert
                let dict_localhost_server = dictServersInfo?dictServersInfo:{"123456789":{host:'wss://localhost',port:'3001',path:'/game'}};//QUITAR
                populateListServers(dict_localhost_server);//QUITAR
                return;
            }
            populateListServers(dictServersInfo);
        } catch (error) {
            console.error('Error loading server information:', error);
        } finally {
            hideLoadingScreen();
        }
    });
    
}

document.getElementById('selectPort')?.addEventListener('click', selectPortRequest);

document.getElementById('formStartWebSocketServer')?.addEventListener('submit', funcStartWebSocketServer);
function setupEventListeners() {    
    let command;

    document.getElementById('startWebsocketServer')?.addEventListener('click', function(event){
        showLoadingScreen();
        event.preventDefault();
        let form = document.getElementById('formStartWebSocketServer')
        let host_ = form.elements['host'].value;
        let port_ = form.elements['ports'].value;
        let path_ = form.elements['path'].value;
        let game_id_ = form.elements['gameId'].value;
        let game_name_ = form.elements['game_name'].value;
        config = {
            game_name:game_name_,
            user_nickname:user_nickname,
            game_id:game_id_,
            host:host_,
            port:port_,
            path:path_
        }
        startWebSocketServer(config)
    })
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
            const serversInfo = await getInfoFromServers('websocket_tasks');
            populateListServers(serversInfo);
        } catch (error) {
            console.error('Error loading server information:', error);
        }finally{
            hideLoadingScreen()
        }
    });
}
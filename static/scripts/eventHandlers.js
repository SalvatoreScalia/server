function setupEventListeners() {    
    let command;

    document.getElementById('startWebsocketServer')?.addEventListener('submit', function(event){
        event.preventDefault();
        showLoadingScreen();
        let form = document.getElementById('formStartWebSocketServer')
        let host_ = form.elements['host'].value;
        let port_ = form.elements['port'].value;
        let path_ = form.elements['path'].value;
        let game_id_ = form.elements['gameId'].value;
        let game_name_ = form.elements['game_name'].value;
        let user_nickname = localStorage.getItem('user_nickname') || 'Guest';
        config = {
            game_name:game_name_,
            user_nickname:user_nickname,
            game_id:game_id_,
            host:host_,
            port:port_,
            path:path_
        }
        startWebSocketServer(config)
    });
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
            const serversInfo = await getInfoFromServer('websocket_tasks');
            populateListServers(serversInfo);
        } catch (error) {
            console.error('Error loading server information:', error);
            hideLoadingScreen();
        }finally{
            hideLoadingScreen();
        }
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
}
function setupEventListeners() {    
    let command;

    document.getElementById('startWebsocketServer')?.addEventListener('click', async function(event){
        try{
            showLoadingScreen()
            port = ':8080';
            path = '/start_websocket';
            config = true;
            dict = {foo:"bar"}
            const response = await fetch(url+port+path,{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({config,dict})
            });
            
            const data = await response.json();
            
            if(response.ok){
                console.log(data.message);
                try{
                    connectWebSocket("/game");
                } catch (error){
                    console.log('Error after start websocket with path game: ',error);
                }
            }else{
                console.log('The server not response ok.');
            }
        } catch (error){
            console.log("Error when send command start_websocket.");
            hideLoadingScreen();
        }finally{
            hideLoadingScreen();
        }
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
        command = JSON.stringify({ command: '/updateState', index: 0, text: "" });
        WebSocketService.sendCommand(command);
    });
    document.getElementById('reconnectButton')?.addEventListener('click', function() {
        reconnectSockets("/game");
    });
    document.getElementById('toggleScrollButton')?.addEventListener('click',function(){
        toggleAutoScroll(this);
    })
    document.getElementById('clearBufferButton')?.addEventListener('click', function() {
        clearBuffer(0);
    });
    document.getElementById('logoutButton')?.addEventListener('click', function() {
        localStorage.clear() //removeItem('userRole');
        window.location.href = 'login.html';
    });
}
function setupEventListeners() {    
    let command;

    document.getElementById('startWebsocketServer')?.addEventListener('click', async function(){
        try{
            showLoadingScreen();
            let url = "https://d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev";
            let port = ':8080';
            let path = '/start_websocket';
            config = true;
            dict = {foo:"bar"};
            
            // Define el tiempo máximo de espera para la solicitud en milisegundos
            const timeout = 5000; // 5 segundos

            const fetchWithTimeout = (url, options, timeout) => {
                return Promise.race([
                    fetch(url, options),
                    new Promise((_, reject) => 
                        setTimeout(() => reject(new Error(`Request timed out: ${timeout} ms`,)), timeout)
                    )
                ]);
            };

            const response = await fetchWithTimeout(url+path, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({config,dict})
            }, timeout);
            
            const data = await response.json();
            
            if(response.ok){
                console.log(data);
            }
        } catch (error){
            console.error("Error when send command start_websocket_:",error);
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
        command = JSON.stringify({ command: '/updateState', index: 0 });
        WebSocketService.sendCommand(command);
    });
    document.getElementById('reconnectButton')?.addEventListener('click', function() {
        reconnectSocket("/game");
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
}
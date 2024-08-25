const url = '//d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev'; // URL base del servidor WebSocket
let  webSocket_client;

function connectWebSocket(port_socket,path) {
    webSocket_client = WebSocketService.connectDataOut(
        ('wss:'+url+port_socket+path),
        (event) => {
            const messageDiv = document.getElementById('messages');
            const message = document.createElement('p');
            message.textContent = `Message received: ${event.data}`;
            messageDiv.appendChild(message);
            if (isAutoScrollEnabled()) {
                const messageContainer = document.getElementsByClassName('messages-container');
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        },
        (event) => hideLoadingScreen(),
        (event) => console.error('[webSocketClient]Error connecting to websocket server:', event),
        (event) => {
            console.warn('[webSocketClient]Websocket connection closed:', event);
            hideLoadingScreen();
        }
    );
}

function reconnectSocket(port_socket,path) {
    if(webSocket_client != undefined ){
        if (webSocket_client.readyState === WebSocket.CLOSED) {
            console.log('Reconnecting socket...');
            showLoadingScreen(); // Descomenta esta línea si tienes una función de pantalla de carga
            connectWebSocket(port_socket,path);
        } else {
            console.log(`[webSocketClient]You are now connected... (websocket.readystate: ${webSocket_client.readyState})`);
        }
    }
    else{
        console.warn('[webSocketClient]You must connect to at least one game first or the game has not started yet... GameName:',path);
    }
}

async function fetchWithTimeout(url, options, timeout) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error(`Request timed out: ${timeout} ms`)), timeout)
        )
    ]);
}

async function startWebSocketServer(configServer) {
    console.log(url);
    const port = ':8080';
    const path = '/start_websocket';
    const timeout = 5000; // 5 segundos

    try {
        const response = await fetchWithTimeout('https:'+url + port + path, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(configServer)
        }, timeout);

        if (response.ok) {
            const data = await response.json();
            console.log(data);
        } else {
            console.error("Failed to start WebSocket server:", response.statusText);
        }
    } catch (error) {
        console.error("Error when sending start_websocket command:", error);
    } finally {
        hideLoadingScreen();
    }
}

async function getInfoFromServer(getInfo) {
    const port = ':8080';
    const path = '/get_';
    const timeout = 2000; // 2 segundos

    try {
        const response = await fetchWithTimeout('https:'+url + port + path, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({'get_':getInfo})
        }, timeout);

        if (response.ok) {
            const data = await response.json();
            console.log(data);
            return data;
        } else {
            console.error("Failed to get info from server:", response.statusText);
        }
    } catch (error) {
        console.error("Error when sending get_ command:", error);
        hideLoadingScreen();
    } finally {
        hideLoadingScreen();
    }
}
const wss_url = 'wss://d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev'; // URL base del servidor WebSocket
let  webSocket_client;

const WebSocketService = (function() {
    let socketData = null;

    function connectDataOut(url_port_path, onMessage,onOpen, onError, onClose) {
        socketData = new WebSocket(url_port_path);
        socketData.onmessage = onMessage;
        socketData.onopen = onOpen
        socketData.onerror = onError;
        socketData.onclose = onClose;
        return socketData;
    }

    function sendCommand(command) {
        if (socketData && socketData.readyState === WebSocket.OPEN) {
            socketData.send(command);
        } else {
            console.error('[webSocketService]The connection to the command path server is not open.');
        }
    }

    return {
        connectDataOut: connectDataOut,
        sendCommand: sendCommand
    };
})();

function connectWebSocket(port_socket,path) {
    webSocket_client = WebSocketService.connectDataOut(
        (wss_url+port_socket+path),
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
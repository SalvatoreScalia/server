const url = 'wss://d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev'; // URL base del servidor WebSocket
const port_socket = ':3001';
let  socketData;

function connectWebSocket(path,doc) {
    socketData = WebSocketService.connectDataOut(
        (url+port_socket+path),
        (event) => {
            const messageDiv = doc.getElementById('messages');
            const message = doc.createElement('p');
            message.textContent = `Message received: ${event.data}`;
            messageDiv.appendChild(message);
            if (isAutoScrollEnabled()) {
                const messageContainer = doc.getElementById('messages-container');
                messageContainer.scrollTop = messageContainer.scrollHeight;
            }
        },
        (event) => hideLoadingScreen(),
        (event) => console.error('Error connecting to websocket server:', event),
        (event) => {
            console.warn('Websocket connection closed:', event);
            hideLoadingScreen();
        }
    );
}

function reconnectSocket(path) {
    if(socketData != undefined ){
        if (socketData.readyState === WebSocket.CLOSED) {
            console.log('Reconnecting socket...');
            showLoadingScreen(); // Descomenta esta línea si tienes una función de pantalla de carga
            connectWebSocket(path);
        } else {
            console.log(`You are now connected... (websocket.readystate: ${socketData.readyState})`);
        }
    }
    else{
        console.warn('The game is not begin to...  Name gmae: ',path);
    }
}
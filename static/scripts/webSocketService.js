const WebSocketService = (function() {
    let socketData = null;

    function connectDataInOut(url, onMessage,onOpen, onError, onClose) {
        socketData = new WebSocket(url);
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
            console.error('La conexión con el servidor de comandos no está abierta.');
        }
    }

    return {
        connectDataInOut: connectDataInOut,
        sendCommand: sendCommand
    };
})();


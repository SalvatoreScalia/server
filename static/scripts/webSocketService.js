const WebSocketService = (function() {
    let socketData = null;

    function connectDataOut(url, onMessage,onOpen, onError, onClose) {
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
            console.error('[webSocketService]The connection to the command path server is not open.');
        }
    }

    return {
        connectDataOut: connectDataOut,
        sendCommand: sendCommand
    };
})();


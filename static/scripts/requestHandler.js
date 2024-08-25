const http_url = 'https://d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev/';

async function fetchWithTimeout(url, options, timeout) {
    return Promise.race([
        fetch(url, options),
        new Promise((_, reject) => 
            setTimeout(() => reject(new Error(`Request timed out: ${timeout} ms`)), timeout)
        )
    ]);
}

async function startWebSocketServer(configServer) {
    const port = ':8080';
    const path = '/start_websocket';
    const timeout = 5000; // 5 segundos
    console.log('[WebSocketClient]start '+http_url+ path);
    try {
        const response = await fetchWithTimeout(http_url + path, {
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

async function getInfoFromServer(data_mapping) {
    const port = ':8080';
    const path = '/get_info';
    const timeout = 8000; // 5 seconds
    console.log(http_url + path);
    try {
        const response = await fetchWithTimeout(http_url + path, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({data_mapping})
        }, timeout);

        if (response.ok) {
            const data = await response.json();
            console.log(data);
            return data;
        } else {
            console.warn("Failed to get info from server:", response.statusText);
        }
    } catch (error) {
        console.error("Error when sending get_ command:", error);
        hideLoadingScreen();
    } finally {
        hideLoadingScreen();
    }
}
const http_url = 'https://d3313e93-240b-45e4-be44-0ad52901106a-00-1r2w1zvo1mk1h.worf.replit.dev';

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

async function getInfoFromServer(key) {
    console.log(key)
    let port = ':8080';
    let path = '/get_info';
    let timeout = 8000; // 8 seconds
    let urlWithParams = `${http_url}${path}/${key}`;

    console.log(urlWithParams);

    try {
        const response = await fetchWithTimeout(urlWithParams, {
            method: 'GET',
            headers: {'Content-Type': 'application/json'}
        }, timeout);

        if (response.ok) {
            const data = await response.json();
            console.log(data);
            hideLoadingScreen();
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

async function selectPortRequest() {
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
}
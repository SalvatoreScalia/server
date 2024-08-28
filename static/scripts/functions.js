let autoScroll = true;
const langStrings = JSON.parse(localStorage.getItem('langStrings'));

function showLoadingScreen() {
    document.getElementById('loading-container').style.display = 'flex';
}

function hideLoadingScreen() {
    document.getElementById('loading-container').style.display = 'none';
}

function clearBuffer(numberOfLinesStartToEnd) {
    const mensajesDiv = document.getElementById('messages');
    while (mensajesDiv.childElementCount > numberOfLinesStartToEnd) {
        mensajesDiv.removeChild(mensajesDiv.firstChild);
    }
    console.log(langStrings.clearBufferMessage);
}

function toggleAutoScroll(button) {
    autoScroll = !autoScroll;
    button.textContent = autoScroll ? 'Desactivar Auto-scroll' : 'Activar Auto-scroll';
    console.log(`Auto-scroll ${autoScroll ? 'enabled' : 'disabled'}.`);
}

function isAutoScrollEnabled() {
    return autoScroll;
}

/**
 * Replaces placeholders in a string with values from a replacements object.
 * @param {string} template - The string containing placeholders.
 * @param {Object} replacements - An object with keys corresponding to placeholder names.
 * @returns {string} - The resulting string with placeholders replaced.
 */
function replacePlaceholders(template, replacements) {
    return template.replace(/{{(\w+)}}/g, (match, key) => {
        return typeof replacements[key] !== 'undefined' ? replacements[key] : match;
    });
}

function populatePorts(listAvailablePorts) {
    // Get the select element where options will be injected
    let selectPort = document.getElementById('selectPort');

    // Clear any existing options in the select (optional)
    selectPort.innerHTML = '';

    // Check if the list of ports is valid
    if (listAvailablePorts && listAvailablePorts.length > 0) {
        listAvailablePorts.forEach(function(port) {
            // Create a new option element
            let option = document.createElement('option');
            option.value = port;
            option.textContent = port;

            // Append the option to the select element
            selectPort.appendChild(option);
        });
    } else {
        // If no ports are available, you can add a default option or leave the select empty
        let option = document.createElement('option');
        option.value = '';
        option.textContent = 'No available ports';
        selectPort.appendChild(option);
    }
}

function populateListServers(servers) {
    const serversDiv = document.getElementById('servers');

    // Clear any existing content in the servers div
    serversDiv.innerHTML = '';

    // Iterate over the dictionary `listServers`
    for (const [key, server] of Object.entries(servers)) {
        // Create a container for each server
        const serverContainer = document.createElement('div');
        serverContainer.classList.add('server-container');

        // Create a paragraph element to display server information
        const serverInfo = document.createElement('p');
        let fDate = formatStringDate(server.start_time);
        serverInfo.textContent = `Name: ${server.game_name} | Start Time: ${fDate} | Host: ${server.host} | Port: ${server.port} | Path: ${server.path} | Players: ${server.players}`;

        // Create the "Join" button
        const joinButton = document.createElement('button');
        joinButton.textContent = 'Join';
        joinButton.style.marginRight = '4px';
        joinButton.onclick = () => {
            joinServer(server.host,server.port,server.path);
        };

        // Append server information and the button to the server container
        serverContainer.appendChild(joinButton);
        serverContainer.appendChild(serverInfo);

        // Append the server container to the servers div
        serverContainer.style.margin = '2px';
        serversDiv.appendChild(serverContainer);
    }
}


function formatStringDate(serverTime){
    let dateObj = new Date(serverTime);
    let hours = dateObj.getHours().toString().padStart(2, '0');
    let minutes = dateObj.getMinutes().toString().padStart(2, '0');
    let day = dateObj.getDate().toString().padStart(2, '0');
    let month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    let year = dateObj.getFullYear();
    
    let formattedTime = `${hours}:${minutes} - ${day}/${month}/${year}`;
    return formattedTime;
}

function joinServer(h,port,path){
    localStorage.removeItem('wss_port');
    localStorage.removeItem('wss_path');
    localStorage.setItem('wss_port',port);
    localStorage.setItem('wss_path',path);
    //connectWebSocket(':'+`${port}`,path);
    connectWebSocket(':'+`${port}`,path);
}

function funcStartWebSocketServer(event){
    event.preventDefault();
    showLoadingScreen();
    let form = document.getElementById('formStartWebSocketServer')
    let host_ = form.elements['host'].value;
    let port_ = form.elements['selectPort'].value;
    let path_ = form.elements['path'].value;
    let file_name_ = form.elements['file_name'].value;
    let game_name_ = form.elements['game_name'].value;
    let user_nickname_ = localStorage.getItem('user_nickname') || 'Guest';
    const config = {
        game_name:game_name_,
        user_nickname:user_nickname_,
        file_name:file_name_,
        host:host_,
        port:port_,
    }
    if (path_) {
        config.path = path_;
    }
    startWebSocketServer(config)
}
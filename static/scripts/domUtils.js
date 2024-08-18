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
const userLanguageRegion = navigator.language || navigator.userLanguage;
const lang = userLanguageRegion.split('-')[0];
console.log("Current language:",lang); // Por ejemplo, "en"
selectLanguageStrings(lang);

// Function to load the language JSON file
function selectLanguageStrings(language) {
    switch (language) {
        case 'es':
            return loadStringsFromFile('es.json');
        case 'it':
            return loadStringsFromFile('it.json');
        case 'de':
            return loadStringsFromFile('de.json');
        default:
            return loadStringsFromFile('en.json');
    }
}

// Function to load the language JSON file
async function loadStringsFromFile(language) {
    try {
        const response = await fetch(`../res/${language}`);
        if (!response.ok) {
            throw new Error(`Could not load language file: ${response.statusText}`);
        }
        const data = await response.json();
        localStorage.setItem("langStrings", JSON.stringify(data));
        console.log('Success loading language strings!')
        return data;
    } catch (error) {
        console.warn('Error loading language strings:', error);
        // Fallback to English if there is an error
        return await loadFallbackLanguageFromFile();
    }
}

// Function to load the fallback language JSON file (English in this case)
async function loadFallbackLanguageFromFile() {
    try {
        const response = await fetch(`../res/es.json`);
        if (!response.ok) {
            throw new Error(`Could not load fallback language file: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('Success loading Fallback (es) strings!')
        localStorage.setItem("langStrings", JSON.stringify(data));
        return data;
    } catch (error) {
        console.error('Error loading fallback language strings from file: es.json.', error);
        return {};
    }
}
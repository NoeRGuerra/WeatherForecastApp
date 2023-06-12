document.getElementById("submit_button").addEventListener("click", validateForm);

function validateForm(event) {
    event.preventDefault(); // Prevent form submission

    const form = document.getElementById('api_form');
    const api_key = document.getElementById("api_key_input").value;

    console.log(form);
    validateApiKey(api_key).then(isValid => {
        if (isValid) {
            form.submit();
        }
    });
}

const API_KEY_LENGTH = 32;

function validateApiKey(api_key) {
    clearErrorMessage();
    if (api_key.length != API_KEY_LENGTH) {
        console.log("Invalid API Key.");
        displayErrorMessage("Error: Wrong API key length");
        return Promise.resolve(false);
    }

    const apiUrl = `https://api.openweathermap.org/data/2.5/weather?q=London&appid=${api_key}`;
    return fetch(apiUrl)
        .then(response => {
            if (response.ok) {
                console.log('API key is valid.');
                return true;
            } else {
                console.log('Invalid API key.');
                displayErrorMessage('Invalid API key.')
                return false;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            displayErrorMessage('Error:', error)
            return false;
        });
}

function validateApiLength() {
    var apiKeyInput = document.getElementById('api_key_input');

    apiKeyInput.addEventListener('input', function (event) {
        var apiKey = event.target.value;
        if (apiKey.length > API_KEY_LENGTH) {
            event.target.value = apiKey.slice(0, -1);
        }
    })
}

function displayErrorMessage(message) {
    const errorMessageContainer = document.getElementById("error_message");
    errorMessageContainer.textContent = message;
    errorMessageContainer.style.display = "block";
}

function clearErrorMessage() {
    const errorMessageContainer = document.getElementById("error_message");
    errorMessageContainer.textContent = "";
    errorMessageContainer.style.display = "none";
}
document.getElementById("submit_button").addEventListener("click", validateForm);

function validateForm(event) {
    event.preventDefault(); // Prevent form submission

    const zipCode = document.getElementById("zip_code_input").value;
    const country = document.getElementById("country_list").value;

    // Perform ZIP code and country validation
    // showLoadingState(); // Show loading state

    validateZipCodeCountry(zipCode, country)
        .finally(() => {
            hideLoadingState(); // Hide loading state
        });;
}

function createTargetUrl(latitude, longitude) {
    const pageUrl = `${APP_PATH}/weather/lat=${latitude}&lon=${longitude}`;
    window.location.href = pageUrl;
}

function validateZipCodeCountry(zipCode, country) {
    const nominatimUrl = `https://nominatim.openstreetmap.org/search?postalcode=${zipCode}&country=${country}&format=json&addressdetails=1&limit=1`;
    clearErrorMessage();

    fetch(nominatimUrl)
        .then((response) => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Error in API response');
            }
        })
        .then((data) => {
            if (data.length > 0) {
                const foundCountryCode = data[0].address.country_code.toUpperCase();
                if (foundCountryCode === country) {
                    // ZIP code belongs to the specified country
                    // Proceed with form submission or further processing
                    const latitude = parseFloat(data[0].lat);
                    const longitude = parseFloat(data[0].lon);

                    console.log("ZIP code belongs to the specified country");
                    document.getElementById("zip_code_input").classList.remove("invalid");
                    createTargetUrl(latitude, longitude);
                } else {
                    // ZIP code does not belong to the specified country
                    console.log("ZIP code does not belong to the specified country");
                    document.getElementById("zip_code_input").classList.add("invalid");
                }
            } else {
                // ZIP code not found
                console.log("ZIP code not found");
                document.getElementById("zip_code_input").classList.add("invalid");
                displayErrorMessage("Error: Failed to fetch coordinates. Please try again.");
            }
        })
        .catch((error) => {
            // Error in API request
            console.log("Error in API request:", error);
            document.getElementById("zip_code_input").classList.add("invalid");
        });
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

function showLoadingState() {
    // Disable the submit button
    document.getElementById("submit_button").disabled = true;
    // Show a loading indicator or message
    // For example, you can add a spinner element to your HTML and show it:
    document.getElementById("loading_spinner").style.display = "block";
}

function hideLoadingState() {
    // Enable the submit button
    document.getElementById("submit_button").disabled = false;
    // Hide the loading indicator or message
    // For example, if you added a spinner element, you can hide it:
    document.getElementById("loading_spinner").style.display = "none";
}


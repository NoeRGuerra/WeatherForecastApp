function showLocation(position) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;
  const pageUrl = `/weather/lat=${lat}&lon=${lon}`;
  window.location.href = pageUrl;
}

function showError(error) {
  console.error(error.message);
}

function getUserLocation() {
  navigator.geolocation.getCurrentPosition(showLocation, showError);
}

window.addEventListener('load', getUserLocation);

function validateZipCode() {
  var zipCodeInput = document.getElementById('zip_code_input');
  var maxLength = 6;
  zipCodeInput.addEventListener('input', function (event) {
    var zipCode = event.target.value;
    var numbersRegex = /^[0-9]*$/;
    if (!numbersRegex.test(zipCode) || zipCode.length > maxLength) {
      event.target.value = zipCode.slice(0, -1);
    }
  });
}

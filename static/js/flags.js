$(document).ready(function () {
	function formatOption(country) {
		if (!country.id) {
			return country.text;
		}

		var classes = "fi fi-" + country.element.value.toLowerCase();

		var $country = $('<span class="flag-option"></span>');
		$country.append($('<span class="' + classes + '"></span>'));
		$country.append(document.createTextNode(" " + country.text));

		return $country;
	}


	$('#country_list').select2({
		placeholder: "Select a country",
		templateResult: formatOption,
		templateSelection: formatOption
	});
});

$(document).on("select2:open", () => {
	document.querySelector(".select2-container--open .select2-search__field").focus()
})
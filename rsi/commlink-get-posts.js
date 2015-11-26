page = 0;
content = [];
getNext = function(response) {
	if (response === undefined) {
		console.log("Aborting");
		return;
	}
	if (response.data.indexOf('<div class="no-results">') == 0) {
		console.log("Download finished on page " + page);
		return;
	}

	window.dump(response.data);
	page++;
	console.log("Querying page " + page);
	RSI.Api.Hub.getCommlinkItems(getNext, {"page": page});
};
RSI.Api.Hub.getCommlinkItems(getNext);

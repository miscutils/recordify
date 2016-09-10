serviceActive = false;

var urlRegex = /^https?:\/\/(?:[^./?#]+\.)?spotify\.com/;
urlRegex = /^.*/; //TODO

var getTrackInfo = function(trackInfo) {
	var enableRecorder = document.getElementById('enableRecorder');
	if(enableRecorder.checked) {
		console.log(trackInfo);
		startRecording(trackInfo);
	}
};

var startStopCallback = function() {
	console.log("startStopCallback");
};

document.addEventListener('DOMContentLoaded', function() {
	var enableRecorder = document.getElementById('enableRecorder');

    chrome.storage.local.get('enableRecorder', function (result) {
		enableRecorder.checked = result.enableRecorder ? "checked" : null;
    });

	enableRecorder.addEventListener('change', function() {
		var value = {'enableRecorder': !!enableRecorder.checked};
		chrome.storage.local.set(value, function() {
			chrome.tabs.getSelected(null, function(tab) {
				if (urlRegex.test(tab.url)) {
					if(enableRecorder.checked) {
						chrome.runtime.sendMessage({text: 'start_recording'}, startStopCallback);
					} else {
						chrome.runtime.sendMessage({text: 'stop_recording'}, startStopCallback);
					}
				}
			});
        });
	}, false);
}, false);

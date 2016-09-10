var channel = null;
var urlRegex = /^https?:\/\/(?:[^./?#]+\.)?spotify\.com/;

var recordingActive = false;

chrome.storage.local.get('enableRecorder', function (result) {
	recordingActive = result.enableRecorder;
});

var getChannel = function() {
	if(!channel) {
		try {
			channel = chrome.runtime.connectNative('miscutils.recordify.host');
			channel.onMessage.addListener(function(msg) {
				if(!msg || msg.result != 'ok') {
					console.log("Received", msg);
				}
			});
			channel.onDisconnect.addListener(function() {
				console.log("Disconnected");
			});
		} catch(e) {
			console.log(e);
		}
	}
	return channel;
};

chrome.runtime.onMessage.addListener(function(data, sender, sendResponse) {
	if (data) {
		if (data.text === 'start_recording') {
			recordingActive = true;
		} else if (data.text === 'stop_recording') {
			recordingActive = false;
		} else {
			if(recordingActive) {
				getChannel().postMessage(data);
			}
		}
	}
});

"use strict"

var channel = null;
var changeCallback = null;

var children = function(node, name) {
	var result = [];
	var childNodes = node.getElementsByTagName(name);
	for(var i = 0; i < childNodes.length; i += 2) {
		result.push(childNodes[i]);
	}
	return result;
};

var byId = function(id) {
	return document.getElementById(id);
};

var byXPath = function(path) {
	var result = [];
	var tmp = document.evaluate(path, document, null, XPathResult.ANY_TYPE, null);
	var node = tmp.iterateNext(); 
	while (node) {
		result.push(node);
		node = tmp.iterateNext();
	}
	return result;
};

var hasClass = function(element, selector) {
	var className = " " + selector + " ";
	return (" " + element.className + " ").replace(/[\n\t\r]/g, " ").indexOf(className) > -1;
};

function hmsToSec(str) {
    var p = str.split(':'),
    	s = 0, m = 1;
    while (p.length > 0) {
        s += m * parseInt(p.pop(), 10);
        m *= 60;
    }
    return s;
};

var getCover = function() {
	var cover = byId('cover-art');
	if(cover) {
		cover = byXPath("//*[@id='cover-art']/a/div/div/@style");
		if(cover && cover[0]) {
			cover = cover[0].nodeValue.replace(/.*"(.+)".*/, '$1');
			return cover;
		}
	}
	return undefined;
};

var getInfo = function(includeCover) {
	var trackName = byId('track-name');
	var trackArtist = byId('track-artist');
	var position = byId('position');
	var playPause = byId('play-pause');
	var trackCurrent = byId('track-current');
	var trackLength = byId('track-length');
	trackCurrent = trackCurrent ? hmsToSec(trackCurrent.innerText) : -1;
	trackLength = trackLength ? hmsToSec(trackLength.innerText) : -1;
	var artists = [];
	var artistNodes = children(trackArtist, 'a');
	for(var i = 0; i < artistNodes.length; i += 2) {
		artists.push(artistNodes[i].innerText);
	}
	var info = {
		title: trackName ? trackName.innerText : null,
		artist: artists[0],
		artists: artists,
		position: position.style.left,
		trackCurrent: trackCurrent,
		trackLength: trackLength,
		trackPercent: trackCurrent / trackLength,
		playing: hasClass(playPause, 'playing')
	};
	if(includeCover) {
		info.cover = getCover();
	}
	return info;
};

var sendInfo = function(includeCover) {
	var info = getInfo(includeCover);
	var request = { 'current_track': info };
	try {
		console.log("Sending message");
		chrome.runtime.sendMessage(request, function(response) {
			// message sent
 		});
	} catch(e) {
		console.log("Cannot send message. Please reload page.")
	}
};

var observeDOM = (function(){
	var MutationObserver = window.MutationObserver || window.WebKitMutationObserver,
		eventListenerSupported = window.addEventListener;

	return function(obj, callback) {
		if(MutationObserver) {
			var obs = new MutationObserver(function(mutations, observer) {
				callback(mutations);
			});
			obs.observe( obj, { 
				childList: true, subtree: true, characterData: true,
				attributes: true, attributeFilter: ['class']
			});
		}
		else if(eventListenerSupported) {
			obj.addEventListener('DOMNodeInserted', callback, false);
			obj.addEventListener('DOMNodeRemoved', callback, false);
		}
	}
})();

var addListeners = function() {
	var player = byId('wrap');
	if(player) {
		observeDOM(player, function(mutations) {
			if(mutations.length == 1 && mutations[0].addedNodes.length == 1 && mutations[0].removedNodes.length == 1) {
				if(mutations[0].addedNodes[0].parentNode.id == 'track-current') {
					return;
				}
			}
			for(var i = 0; i < mutations.length; i ++) {
				var m = mutations[i];
				if(m.type == 'childList') {
					if(hasClass(m.target, 'sp-image')) {
						// console.log(m);
						// console.log(getCover());
					}
					if(m.target.id == 'track-name') {
						if(m.addedNodes.length == 1) {
							// console.log(m);
							// console.log(getInfo());
							setTimeout(function() {
								sendInfo(true);
							}, 1000)
						}
					}
				}
			}
			sendInfo(false);
		});
	}
};

addListeners();

# Recordify - A Spotify Music Recorder

Easily record music from Spotify Web player via a Chrome browser plugin.

## Features

Recordify is a Chrome plugin that automatically records music tracks from Spotify Web player.

* Recording can be easily enabled/disabled via a checkbox that appears in the extensions bar.

* Once the recording mode is enabled, recordify will store files under the following naming scheme:

```
~/Music/recorded/Air/Air - All I Need.mp3
~/Music/recorded/Air/Air - Alone in Kyoto.mp3
~/Music/recorded/Air/Air - Alpha Beta Gaga.mp3
~/Music/recorded/Air/Air - Another day.mp3
~/Music/recorded/Air/Air - Biological.mp3
~/Music/recorded/Air/Air - Cherry Blossom Girl.mp3
~/Music/recorded/Air/Air - Kelly Watch The Stars.mp3
...
```

* ID3 tags (artist, title, album, etc.) are automatically extracted from Spotify and added to the MP3 files.

* Album covers can be automatically downloaded and embedded to the metadata of the MP3 files.

## Prerequisites

Recordify currently works only for Mac OSX. A port for Linux is currently being developed.

Required software:
* Google Chrome browser
* Soundflower (Mac driver for audio recording and multi-device output)
* `python` (version 2.5+)
* `sox` (the "the Swiss Army knife of sound")
* `lame` (audio encoder for Mac)
* `mid3v2` (ID3 tag editor for Mac)
* `wget`

System sound must be configured to play via a Soundflower virtual audio interface. Under Mac
OSX, use the "Audio MIDI Setup" toolkit to create a Multi-Output Device which forwards
the local audio to a virtual Soundflower audio device (named "Soundflower (2ch)"),
in addition to your speakers/headphones.

## Installation

Install the required dependencies and build the code:

```
make build
```

Install the recording server (a Python application) as a native messaging host in Chrome:

```
make install
```

Finally, navigate to `chrome://extensions/` in Chrome, enable "Developer mode", then use the button
"Load unpacked extension..." to add the code directory of Recordify as a developer extension:

## Configuration

t.b.a.

## Disclaimer

This software does not promote any form of piracy or illegal activity. Note that it is solely
your own responsibility to check your user/license agreements with Spotify and verify that the
use of this software is legal under these agreements.

## License

Licensed under the MIT License (see LICENSE file).

#!/usr/bin/env python

"""
Native messaging host for Chrome extension.
"""

import struct
import sys
import threading
import subprocess
import json
import time
import datetime
import os
import sys
import math
import signal
from os.path import expanduser
import unicodedata
import codecs

# export PYTHONPATH
VENV_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '.venv'))
if os.path.isdir(VENV_DIR):
  additional_path = os.path.join(VENV_DIR, 'lib', 'python2.7', 'site-packages')
  if not additional_path in sys.path:
    sys.path.insert(0, additional_path)

# On Windows, the default I/O mode is O_TEXT. Set this to O_BINARY
# to avoid unwanted modifications of the input/output streams.
if sys.platform == "win32":
  import os, msvcrt
  msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
  msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# Configurations
HOME = expanduser("~")
TARGET_FOLDER = "%s/Music/recorded" % HOME
LOG_FILE = "/tmp/spotify.recorder.log"
CMD_SOX = 'sox'
CMD_MID3V2 = 'mid3v2'
CMD_LAME = 'lame'
CMD_WGET = 'wget'
TMP_COVER_FILE_PREFIX = '/tmp/cover.'
# maximum amount to allow a file to be truncated or too long to discard it
MAX_TIME_DIFF_SECS = 7
# whether to overwrite files with the same name
OVERWRITE_FILES = False
# whether to apply ID3 tags with album art image data
APPLY_IMAGE_TAG = False
# whether to kill all sox processes on startup
KILLALL_SOX_ON_STARTUP = False
# audio device to use for recording
RECORDING_AUDIO_DEVICE = 'Soundflower (2c'

# Constants
CODEC_HANDLER_UNDERSCORE = 'underscore'

# global variable for recording thread
recording_thread = None

def codec_error_handler_underscore(e):
  return (u'-', e.start + 1)
# register function as codec error handler
codecs.register_error(CODEC_HANDLER_UNDERSCORE, codec_error_handler_underscore)

def log(line):
  write_file(LOG_FILE, "%s\n" % (line), append=True)

def write_file(file, content, append=False):
  f = open(file, 'a' if append else 'w+')
  f.write(content)
  f.close()

def run_sync(cmd):
  return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)

def run(cmd, wait=False):
  result = subprocess.Popen(cmd, shell=True, stderr=subprocess.STDOUT)
  if wait:
    result.wait()
  return result

def now():
  return time.mktime(datetime.datetime.now().timetuple())

def start_thread(func, param):
  class MyThread (threading.Thread):
    def __init__(self, param):
      threading.Thread.__init__(self)
      self.param = param
      self.result = None
      self.startTime = now()
    def run(self):
      self.result = func(self.param)
  t = MyThread(param)
  t.start()
  # Sleep 1 sec (for self.result to be assigned). TODO find better fix
  time.sleep(1)
  return t

def track_equals(t1, t2):
  return t1 and t2 and \
    t1['artist'] == t2['artist'] and \
    t1['title'] == t2['title'] and \
    t1['album'] == t2['album']

# Helper function that sends a message to the webapp.
def send_message(message):
   # Write message size.
  sys.stdout.write(struct.pack('I', len(message)))
  # Write the message itself.
  sys.stdout.write(message)
  sys.stdout.flush()

def remove_non_ascii(text):
    return unicodedata.normalize('NFKD', text).encode('ascii',CODEC_HANDLER_UNDERSCORE)

def esc(string):
  string = string.replace("'", '_')
  string = remove_non_ascii(string)
  return string

def delete_incomplete_track(info, startTime):
  global recording_thread
  timeNow = now()
  recordingDuration = (timeNow - startTime)
  expectedLength = info['length']
  diff = abs(recordingDuration - expectedLength)
  if diff > MAX_TIME_DIFF_SECS:
    outfile = info['outfile']
    log("Deleting corrupted/incomplete file %s" % outfile)
    os.remove(outfile)

def apply_tags():
  info = recording_thread.param
  cmd = "%s --artist='%s' --album='%s' --song='%s' '%s'" % \
    (CMD_MID3V2, info['artist'], info['album'], info['title'], info['outfile'])
  run(cmd, wait=True)
  coverfile = get_cover_filename(info)
  if os.path.isfile(coverfile) and APPLY_IMAGE_TAG:
    cmd = "%s --ti='%s' '%s'" % (CMD_LAME, coverfile, info['outfile'])
    log("TAG: %s" % cmd)
    run(cmd, wait=True)

def md5(string):
  import hashlib
  m = hashlib.md5()
  m.update(string)
  return m.hexdigest()

def get_cover_filename(info):
  filehash = md5(info['artist'] + info['album'] + info['title'])
  return '%s%s' % (TMP_COVER_FILE_PREFIX, filehash)

def download_cover(info):
  cover = info['cover']
  if not cover:
    return
  coverfile = get_cover_filename(info)
  if not os.path.isfile(coverfile):
    log("Downloading %s to %s" % (cover,coverfile))
    run("%s '%s' -O '%s'" % (CMD_WGET, cover, coverfile))

def stop_recording():
  global recording_thread
  if not recording_thread or not recording_thread.result:
    return
  pid = recording_thread.result.pid
  log("STOP Killing PID %s" % (pid))
  os.kill(pid, signal.SIGTERM)
  oldInfo = recording_thread.param
  startTime = recording_thread.startTime
  recording_thread.result.kill()
  apply_tags()
  recording_thread = None
  delete_incomplete_track(oldInfo, startTime)

def do_start_recording(info):
  outfile = info['outfile']
  cmd = "%s -t coreaudio '%s' -q '%s'" % (CMD_SOX, RECORDING_AUDIO_DEVICE, outfile)
  log('START: %s' % cmd)
  return run(cmd)

def start_recording(info):
  global recording_thread
  if recording_thread:
    if track_equals(info, recording_thread.param):
      log('Track %s already recording atm' % info)
      return
    else:
      stop_recording()
  # make sure the target directory exists
  run("mkdir -p '%s'" % info['outpath']).wait()
  # start the recording thread
  recording_thread = start_thread(do_start_recording, info)

def read_loop():
  if KILLALL_SOX_ON_STARTUP:
    log('Killing all existing sox processes to avoid zombies')
    run('killall sox')
  while 1:
    try:
      # Read the message length (first 4 bytes).
      text_length_bytes = sys.stdin.read(4)
      if len(text_length_bytes) == 0:
        sys.exit(0)
      # Unpack message length as 4 byte integer.
      text_length = struct.unpack('i', text_length_bytes)[0]
      text = sys.stdin.read(text_length).decode('utf-8')

      obj = json.loads(text)

      if 'current_track' in obj:
        track = obj['current_track']
        if track and track['playing']:
          artist = esc(track['artist']) if 'artist' in track else 'Unknown Artist'
          title = esc(track['title']) if 'title' in track else 'Unknown Title'
          album = esc(track['album']) if 'album' in track else ''
          album_str = ('- %s' % album) if album != '' else ''
          length = track['trackLength'] if 'trackLength' in track else -1
          cover = track['cover'] if 'cover' in track else None
          trackCurrent = track['trackCurrent'] if 'trackCurrent' in track else 0
          outpath = '%s/%s' % (TARGET_FOLDER, artist)
          outfile = '%s/%s %s- %s.mp3' % (outpath, artist, album_str, title)
          info = {
            'artist': artist,
            'title': title,
            'album': album,
            'length': length,
            'cover': cover,
            'outfile': outfile,
            'outpath': outpath
          }
          if trackCurrent < MAX_TIME_DIFF_SECS:
            if OVERWRITE_FILES or not os.path.isfile(outfile):
              start_recording(info)
            else:
              log('File already exists, skipping: %s' % outfile)
          if cover:
            # download the album cover
            download_cover(info)
        else:
          stop_recording()
      else:
        log("Expected 'current_track' in %s" % obj)

      send_message('{"result": "ok"}')
    except Exception, e:
      send_message('{"error": "%s"}' % e)

def setup():
  run("mkdir -p '%s'" % TARGET_FOLDER)

def main():
  setup()
  read_loop()
  sys.exit(0)


if __name__ == '__main__':
  main()

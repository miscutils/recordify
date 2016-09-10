#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd )"
source $DIR/config.sh

HOST_NAME=miscutils.recordify.host
rm "$TARGET_DIR/$HOST_NAME.json"
echo "Native messaging host $HOST_NAME has been uninstalled."

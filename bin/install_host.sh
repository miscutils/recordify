#!/bin/sh

DIR="$( cd "$( dirname "$0" )" && pwd )"
source $DIR/config.sh

HOST_NAME=miscutils.recordify.host

# Create directory to store native messaging host.
mkdir -p "$TARGET_DIR"

# Copy native messaging host manifest.
cp "$DIR/../host/$HOST_NAME.json" "$TARGET_DIR"

# Update host path in the manifest.
HOST_PATH=$DIR/../host/host.py
ESCAPED_HOST_PATH=${HOST_PATH////\\/}
sed -i -e "s/HOST_PATH/$ESCAPED_HOST_PATH/" "$TARGET_DIR/$HOST_NAME.json"

# Set permissions for the manifest so that all users can read it.
chmod o+r "$TARGET_DIR/$HOST_NAME.json"

echo "Native messaging host $HOST_NAME has been installed."

#!/bin/bash

THIS_SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

xhost +local:docker # forward X11
docker run \
   --network host \
   --name $USER-ardupilot-mavlink-gui-container \
   -e DISPLAY=$DISPLAY \
   -v /tmp/.X11-unix:/tmp/.X11-unix \
   -v "$(dirname "$PWD"):/ardupilot-mavlink-gui" \
   -it \
   --rm \
   ardupilot-mavlink-gui:latest \
   bash

#############################################################################
# Sean Hurley (seandhurley@live.com)                                        #
# September 15, 2026                                                        #
#############################################################################
#!/bin/bash -e

SRC="$(dirname $(realpath ${BASH_SOURCE[@]}))"
source $SRC/A-variables.sh

cd ~/lca/voctomix/
./voctocore/voctocore.py -i ~/lca/video-scripts/ryan/lca/config.ini $VOCTOOPTIONS


#!/bin/bash -e

SRC="$(dirname $(realpath ${BASH_SOURCE[@]}))"
source $SRC/A-variables.sh

# requires shared SSH keys to be setup
# and A-variables.sh to be setup relevant to the remote machine

ssh $REMOTEUSER@$REMOTEIP ~/video-scripts/ryan/lca/$REMOTESCRIPT 

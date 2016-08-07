#!/bin/bash -e

dir=$VIDEO_LOCATION/dv/$HOSTNAME/$(date +%Y-%m-%d)
mkdir -p $dir

cd ~/lca/video-scripts/pycon

~/lca/voctomix/example-scripts/control-server/generate-cut-list.py \
  | tee --append $dir/cut-list.log






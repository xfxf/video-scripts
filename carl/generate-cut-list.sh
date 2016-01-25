#!/bin/bash -ex


dir=~/Videos/veyepar/lca/lca2016/dv/$HOSTNAME/$(date +%Y-%m-%d)
mkdir -p $dir

cd ~/lca/video-scripts/carl

~/lca/voctomix/example-scripts/control-server/generate-cut-list.py \
  | tee --append $dir/cut-list.log






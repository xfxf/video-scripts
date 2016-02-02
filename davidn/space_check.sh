#!/usr/bin/env bash
#
# Check disk space on mixers

declare -a machines
machines=(r1mix r2mix r3mix r4mix r5mix)
login=videoteam

for machine in ${machines[*]}
do

    echo "${machine}: \c"
    ssh ${login}@${machine} 'df -H / | grep -v ^Filesystem'

done

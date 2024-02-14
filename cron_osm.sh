#!/bin/bash

set -e

source /data/project/bano_v3/venv_v3/bin/activate

pip install -e .

source config

lockfile=imposm.lock

echo `date`
echo debut

if test -f ${lockfile}
then
  diff_age=$((`date +%s` - `stat -c %Y $lockfile`))
  if [ $diff_age -gt 7200 ];then
    echo "Effacement du lock"
    rm ${lockfile}
  else
    echo `date`" : Process deja en cours"
    exit 1
  fi
fi


touch ${lockfile}

osmosis --rri workingDirectory=${DOWNLOAD_DIR} --wxc ${DOWNLOAD_DIR}/changes.osc.gz
imposm diff -config imposm.config -dbschema-production osm ${DOWNLOAD_DIR}/changes.osc.gz

rm ${lockfile}

echo `date`
echo fin

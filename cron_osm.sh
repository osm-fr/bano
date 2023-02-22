#!/bin/bash

set -e

source /data/project/bano_v3/venv_v3/bin/activate

pip install -e .

source config

lockfile=imposm.lock

echo `date`>> $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log

if test -f ${lockfile}
then
  diff_age=$((`date +%s` - `stat -c %Y $lockfile`))
  if [ $diff_age -gt 7200 ];then
    echo "Effacement du lock" >> $SCRIPT_DIR/cron.log
    rm ${lockfile}
  else
    echo `date`" : Process deja en cours" >> $SCRIPT_DIR/cron.log
    exit 0
  fi
fi


touch ${lockfile}

osmosis --rri workingDirectory=${DOWNLOAD_DIR} --wxc ${DOWNLOAD_DIR}/changes.osc.gz
imposm diff -config imposm.config -dbschema-production osm ${DOWNLOAD_DIR}/changes.osc.gz

rm ${lockfile}

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

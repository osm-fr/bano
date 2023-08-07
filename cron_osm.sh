#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

lockfile=${SCRIPT_DIR}/imposm.lock

echo `date`>> $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log

if test -f ${lockfile}
then
  diff_age=$((`date +%s` - `stat -c %Y $lockfile`))
  if [ $diff_age -gt 14400 ];then
    echo "Effacement du lock" >> $SCRIPT_DIR/cron.log
    rm ${lockfile}
  else
    echo `date`" : Process deja en cours" >> $SCRIPT_DIR/cron.log
    exit 0
  fi
fi


touch ${lockfile}

osmosis --rri workingDirectory=${DOWNLOAD_DIR} --wxc ${DOWNLOAD_DIR}/changes.osc.gz
imposm diff -config $SCRIPT_DIR/imposm.config -dbschema-production osm ${DOWNLOAD_DIR}/changes.osc.gz

bano update_table_communes

rm ${lockfile}

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

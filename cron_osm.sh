#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

lockfile=${SCRIPT_DIR}/imposm.lock

if test -f ${lockfile}
then
  diff_age=$((`date +%s` - `stat -c %Y $lockfile`))
  # echo $diff_age
  if [ $diff_age -gt 14400 ];then
    rm imposm.lock
  else
    echo `date`" : Process deja en cours"
    exit 0
  fi
fi

echo `date` > $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log

touch ${lockfile}

osmosis --rri workingDirectory=${DOWNLOAD_DIR} --wxc ${DOWNLOAD_DIR}/changes.osc.gz
imposm diff -config $SCRIPT_DIR/imposm.config -dbschema-production osm ${DOWNLOAD_DIR}/changes.osc.gz
#$SCRIPT_DIR/update_table_infos_communes.sh

rm ${lockfile}

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

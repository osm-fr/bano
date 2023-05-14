#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

lockfile=${SCRIPT_DIR}/imposm.lock

if test -f ${lockfile}
then
  echo `date`" : Process deja en cours" >> $SCRIPT_DIR/cron.log
  exit 0
fi

echo `date` > $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log

touch ${lockfile}

osmosis --rri workingDirectory=${DOWNLOAD_DIR} --wxc ${DOWNLOAD_DIR}/changes.osc.gz
imposm diff -config $SCRIPT_DIR/imposm.config -dbschema-production osm -expiretiles-dir $EXPIRE_TILES_DIR -expiretiles-zoom 16 ${DOWNLOAD_DIR}/changes.osc.gz
#$SCRIPT_DIR/update_table_infos_communes.sh

rm ${lockfile}

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

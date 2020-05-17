#!/bin/bash

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

osmosis --rri workingDirectory=/data/download --wxc /data/download/changes.osc.gz
imposm diff -mapping $SCRIPT_DIR/bano.yml -cachedir /data/bano_imposm_cache -dbschema-production public -diffdir /data/bano_imposm_diff -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -expiretiles-dir $EXPIRE_TILES_DIR -expiretiles-zoom 16 /data/download/changes.osc.gz
$SCRIPT_DIR/update_table_infos_communes.sh

rm ${lockfile}

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

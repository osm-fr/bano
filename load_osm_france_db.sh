#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

PBF_URL=${1:-http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf}
PBF_FILE=$(basename "$PBF_URL")

lockfile=${SCRIPT_DIR}/imposm.lock

if test -f ${lockfile}
then
  echo `date`" : Process deja en cours" >> $SCRIPT_DIR/cron.log
  exit 0
fi

touch ${lockfile}

mkdir -p $DOWNLOAD_DIR
cd $DOWNLOAD_DIR
wget -NS $PBF_URL
imposm import -mapping $BANO_DIR/bano.yml -read $DOWNLOAD_DIR/$PBF_FILE -overwritecache -cachedir $IMPOSM_CACHE_DIR -dbschema-import public -diff -diffdir $DOWNLOAD_DIR
imposm import -mapping $BANO_DIR/bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir $IMPOSM_CACHE_DIR -dbschema-import public -diff -diffdir $DOWNLOAD_DIR

psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f $BANO_DIR/sql/finalisation.sql

cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
rm ${lockfile}

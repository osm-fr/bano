#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

PBF_URL=${1:-http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf}
PBF_FILE=$(basename "$PBF_URL")

lockfile=${DATA_DIR}/imposm.lock

if test -f ${lockfile}
then
  echo `date`" : Process deja en cours"
  exit 1
fi

touch ${lockfile}

mkdir -p $DOWNLOAD_DIR
cd $DOWNLOAD_DIR
wget -NS $PBF_URL
imposm import \
  -config $SCRIPT_DIR/imposm.config \
  -read $DOWNLOAD_DIR/$PBF_FILE \
  -overwritecache \
  -cachedir $IMPOSM_CACHE_DIR \
  -diff \
  -write \
  -connection postgis://$PGCON_BANO?prefix=NONE \
  -dbschema-import osm

$pgsql_BANO -f $SCRIPT_DIR/sql/finalisation.sql

cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
rm ${lockfile}

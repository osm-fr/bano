#!/bin/bash

set -e

source config

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
wget --directory-prefix=$DOWNLOAD_DIR -NS $PBF_URL
imposm import \
  -config imposm.config \
  -read $DOWNLOAD_DIR/$PBF_FILE \
  -overwritecache \
  -diff \
  -write \
  -dbschema-import osm

psql -d bano -U cadastre -v ON_ERROR_STOP=1 -f $SCRIPT_DIR/sql/finalisation.sql

cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
rm ${lockfile}

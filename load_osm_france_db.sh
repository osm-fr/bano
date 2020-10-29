#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

cd $DOWNLOAD_DIR
wget -NS http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf
imposm import -mapping $BANO_DIR/bano.yml -read $DOWNLOAD_DIR/france_metro_dom_com_nc.osm.pbf -overwritecache -cachedir $IMPOSM_CACHE_DIR -dbschema-import public -diff -diffdir $DOWNLOAD_DIR
imposm import -mapping $BANO_DIR/bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir $IMPOSM_CACHE_DIR -dbschema-import public -diff -diffdir $DOWNLOAD_DIR

psql -d osm -U cadastre -f $BANO_DIR/sql/finalisation.sql

cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
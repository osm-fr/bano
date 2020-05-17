#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

cd /data/download
wget -NS http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf
imposm import -mapping $BANO_DIR/bano.yml -read /data/download/france_metro_dom_com_nc.osm.pbf -overwritecache -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff
imposm import -mapping $BANO_DIR/bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff

psql -d osm -U cadastre -f $BANO_DIR/sql/finalisation.sql

cp /data/bano_imposm_diff/last.state.txt /data/download/state.txt
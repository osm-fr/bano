#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

echo `date` > $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log
 
osmosis --rri workingDirectory=/data/download --wxc /data/download/changes.osc.gz
imposm diff -mapping $SCRIPT_DIR/bano.yml -cachedir /data/bano_imposm_cache -dbschema-production public -diffdir /data/bano_imposm_diff -connection 'postgis://cadastre@localhost/osm'?prefix=NONE /data/download/changes.osc.gz

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

lockfile=${SCRIPT_DIR}/imposm.lock

if test -f ${lockfile}
then
  echo `date`" : Process deja en cours" >> $SCRIPT_DIR/cron.log
  exit 0
fi

touch ${lockfile}

cd $DOWNLOAD_DIR
wget -NS http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf
imposm import -config $SCRIPT_DIR/imposm.config -read $DOWNLOAD_DIR/france_metro_dom_com_nc.osm.pbf -overwritecache -diff -write -dbschema-import public

psql -d bano_sources -U cadastre -f $BANO_DIR/sql/finalisation.sql

#cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
rm ${lockfile}

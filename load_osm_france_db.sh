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
# Récupère le state.txt
STATE_URL=${PBF_URL/.osm.pbf/.state.txt}
wget -NS $STATE_URL
mv `basename "${STATE_URL}"` state.txt

# Configure osmosis pour les updates
rm -f configuration.txt
osmosis --read-replication-interval-init  workingDirectory=.
REPL=${PBF_URL/extracts/replication/}
REPL=${REPL/.osm.pbf/\/minute/}
sed -i -e "s|baseUrl.*|baseUrl=${REPL}|" configuration.txt
# 5 jours
sed -i -e "s|maxInterval.*|maxInterval=432000|" configuration.txt

imposm import \
  -config $SCRIPT_DIR/imposm.config \
  -read $DOWNLOAD_DIR/$PBF_FILE \
  -overwritecache \
  -cachedir $IMPOSM_CACHE_DIR \
  -diff \
  -write \
  -dbschema-import osm

$pgsql_BANO -f $SCRIPT_DIR/sql/finalisation.sql

cp $DOWNLOAD_DIR/last.state.txt $DOWNLOAD_DIR/state.txt
rm ${lockfile}

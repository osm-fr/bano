#!/bin/bash

#set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $SCRIPT_DIR
pip install -e .

source $SCRIPT_DIR/config

lockfile=${SCRIPT_DIR}/imposm.lock
LOGFILE=${SCRIPT_DIR}/cron.log

echo `date`>> ${LOGFILE}
echo debut >> ${LOGFILE}

if test -f ${lockfile}
then
  diff_age=$((`date +%s` - `stat -c %Y $lockfile`))
  if [ $diff_age -gt 7200 ];then
    echo "Effacement du lock" >> ${LOGFILE}
    rm ${lockfile}
  else
    echo `date`" : Process deja en cours" >> ${LOGFILE}
    exit 0
  fi
fi


touch ${lockfile}

echo `date`" : Osmosis" >> ${LOGFILE}
osmosis --rri workingDirectory=${DOWNLOAD_DIR} --simc --wxc ${DOWNLOAD_DIR}/changes.osc.gz
echo `date`" : Imposm" >> ${LOGFILE}
imposm diff -config $SCRIPT_DIR/imposm.config -cachedir $IMPOSM_CACHE_DIR -dbschema-production osm ${DOWNLOAD_DIR}/changes.osc.gz
echo `date`" : Osm2pgsql" >> ${LOGFILE}
osm2pgsql -a -S osm2pgsql.style -s -l -d bano -U cadastre -p osm2pgsql $DOWNLOAD_DIR/changes.osc.gz

rm ${lockfile}

echo `date` >> ${LOGFILE}
echo fin >> ${LOGFILE}

tail -1000 ${LOGFILE} > foo.bar.foo && mv foo.bar.foo ${LOGFILE}
#!/bin/bash

set -e

source config

cd $CADASTRE_CACHE_DIR
echo "Mise à jour des lieux-dits" > ld.log
date >> ld.log

for DEPT in {01..19} 2A 2B {21..95} {971..974} 976
# for DEPT in {01..03} 2A
do
    URL="https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/${DEPT}/cadastre-${DEPT}-lieux_dits.json.gz"
	wget -NS ${URL} -o wget.log
    HTTP200=`grep '200 OK' wget.log|wc -l`
    if (( ${HTTP200} ))
    then
        echo "Téléchargement des lieux-dits pour le département ${DEPT} OK" >> ld.log
        ZIPFILE=`basename ${URL}`
        JSONFILE=`basename ${ZIPFILE} .gz`
        # echo $URL
        # echo $ZIPFILE
        # echo $JSONFILE
        gzip -dfk ${ZIPFILE}
        mv ${JSONFILE} lieux_dits.json
        # ls -al
        psql -d osm -U cadastre -c "DELETE FROM lieux_dits WHERE insee_com LIKE '${DEPT}%';"
        ogr2ogr  -append -nln lieux_dits -fieldmap 1,0,2,3 -f PostgreSQL PG:'user=cadastre dbname=osm' lieux_dits.json
        rm lieux_dits.json
    else
        echo "Pas de source plus à jour pour ${DEPT}" >> ld.log
    fi
done

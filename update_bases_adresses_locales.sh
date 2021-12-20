#!/bin/bash
source config

cd $BAL_CACHE_DIR
for dep in {01..19} 2A 2B {21..95} {971..974} 976
# for dep in {01..06} 2A
#for dep in  {24..95} {971..974} 976
do
    echo 'Département '$dep
	wget -NS https://adresse.data.gouv.fr/data/adresses-locales/latest/csv/adresses-locales-$dep.csv.gz
    quoted_dep=\'$dep'%'\'
    psql -d osm -U cadastre -c "DELETE FROM bal_locales WHERE commune_code LIKE $quoted_dep;"
    gunzip -c $BAL_CACHE_DIR/adresses-locales-$dep.csv.gz|psql -d osm -U cadastre -c "\copy bal_locales from stdin with csv header delimiter ';'"
    sleep 1
done

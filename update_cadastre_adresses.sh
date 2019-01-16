#!/bin/bash
source config

for dep in {01..19} 2A 2B {21..95} {971..974} 976
# for dep in {01..03} 2A
#for dep in  {24..95} {971..974} 976
do
    echo 'Département '$dep
	wget https://adresse.data.gouv.fr/data/adresses-cadastre/latest/csv/adresses-cadastre-$dep.csv.gz -O $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv.gz
    quoted_dep=\'$dep'%'\'
    psql -d cadastre -U cadastre -c "DELETE FROM bal_cadastre WHERE commune_code LIKE $quoted_dep;"
    gunzip -c $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv.gz|psql -d cadastre -U cadastre -c "\copy bal_cadastre from stdin with csv header delimiter ';'"
    sleep 1
done

#!/bin/bash
source config

cd $DATA_DIR/bano_cache

#for dep in {01..19} 2A 2B {21..95} {971..974}
#for dep in {01..03} 2A
for dep in  {24..95} {971..974} 976
do
	mkdir $dep
	cd $dep
	full_dep=`pwd`
	wget https://adresse.data.gouv.fr/data/adresses-cadastre/latest/csv/adresses-cadastre-$dep.csv.gz -O $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv.gz
	gunzip $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv.gz
	python $BANO_DIR/dispatch_BAL_adresses.py $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv $full_dep
	gzip $CADASTRE_CACHE_DIR/adresses-cadastre-$dep.csv
    sleep 1
    cd ..
done

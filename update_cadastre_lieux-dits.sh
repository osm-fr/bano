#!/bin/bash
source config

cd $DATA_DIR/bano_cache

for dep in {01..19} 2A 2B {21..95} {971..974} 976
# for dep in {01..03} 2A
#for dep in  {24..95} {971..974} 976
do
	mkdir $dep
	cd $dep
	# full_dep=`pwd`
	wget https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/shp/departements/$dep/cadastre-$dep-lieux_dits-shp.zip -O $CADASTRE_CACHE_DIR/cadastre-$dep-lieux_dits-shp.zip
	unzip $CADASTRE_CACHE_DIR/cadastre-$dep-lieux_dits-shp.zip
    # reconstruction du shapefile avec ogr2ogr car corrompu pour shp2pgsql
    ogr2ogr -overwrite -f 'ESRI Shapefile' lieux_dits_ok.shp lieux_dits.shp
    shp2pgsql -s 2154:4326 -g geometrie -W LATIN1 lieux_dits_ok.shp public.tmp_lieux_dits$dep | psql -d cadastre -U cadastre -q
    psql -d cadastre -U cadastre -f $BANO_DIR/sql/replace_lieux_dits.sql -v schema_cible=$SCHEMA_CIBLE -v dept=$dep
	zip -mT $CADASTRE_CACHE_DIR/cadastre-$dep-lieux_dits-shp.zip lieux_dits.*
    sleep 1
    cd ..
done

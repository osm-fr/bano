#!/bin/bash
source config

cd $DATA_DIR/bano_cache

# for dep in {01..19} 2A 2B {21..95} {971..974} 976
# for dep in {02..03} 2A
for dep in  {04..95} {971..974} 976 2B
do
	mkdir $dep
	cd $dep
	full_dep=`pwd`
	wget https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/shp/departements/$dep/cadastre-$dep-batiments-shp.zip -O $CADASTRE_CACHE_DIR/cadastre-$dep-batiments-shp.zip
	unzip $CADASTRE_CACHE_DIR/cadastre-$dep-batiments-shp.zip
    # reconstruction du shapefile avec ogr2ogr car corrompu pour shp2pgsql
    ogr2ogr -overwrite -f 'ESRI Shapefile' batiments_ok.shp batiments.shp
    shp2pgsql -s 2154:4326 -g geometrie -W LATIN1 batiments_ok.shp public.tmp_batiments$dep | psql -d cadastre -q
    psql -d cadastre -f $BANO_DIR/sql/replace_batiments.sql -v schema_cible=$SCHEMA_CIBLE -v dept=$dep
	zip -mT $CADASTRE_CACHE_DIR/cadastre-$dep-batiments-shp.zip batiments.*
    sleep 1
    cd ..
done

#!/bin/bash

source config
cd $DATA_DIR
mkdir -p cog
cd cog
rm *.csv && rm *.zip
wget -NS https://www.insee.fr/fr/statistiques/fichier/3720946/cog_ensemble_2019_csv.zip
unzip cog_ensemble_2019_csv.zip

CSV_COMMUNE=communes-01042019.csv
CSV_DEPARTEMENT=departement2019.csv

psql -d osm -U cadastre -f $BANO_DIR/sql/create_table_cog.sql
cat ${CSV_COMMUNE}|psql -d osm -U cadastre -c "TRUNCATE TABLE cog_commune;COPY cog_commune FROM stdin WITH csv header delimiter ',';"
cat ${CSV_DEPARTEMENT}|psql -d osm -U cadastre -c "TRUNCATE TABLE cog_departement;COPY cog_departement FROM stdin WITH csv header delimiter ',';"

psql -d cadastre -U cadastre -f $BANO_DIR/sql/create_table_cog.sql
cat ${CSV_COMMUNE}|psql -d cadastre -U cadastre -c "TRUNCATE TABLE cog_commune;COPY cog_commune FROM stdin WITH csv header delimiter ',';"
cat ${CSV_DEPARTEMENT}|psql -d cadastre -U cadastre -c "TRUNCATE TABLE cog_departement;COPY cog_departement FROM stdin WITH csv header delimiter ',';"

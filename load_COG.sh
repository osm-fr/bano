#!/bin/bash

source config
cd $DATA_DIR
mkdir -p cog
cd cog
rm *.csv && rm *2019.zip
wget -NS https://www.insee.fr/fr/statistiques/fichier/3720946/cog_ensemble_2019_csv.zip
unzip cog_ensemble_2019_csv.zip

CSV_COMMUNE=communes-01042019.csv
CSV_CANTON=canton2019.csv
CSV_DEPARTEMENT=departement2019.csv
CSV_REGION=region2019.csv

for d in osm cadastre
do
  psql -d ${d} -U cadastre -f $BANO_DIR/sql/create_table_cog.sql
  cat ${CSV_COMMUNE}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_commune;COPY cog_commune FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_CANTON}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_canton;COPY cog_canton FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_DEPARTEMENT}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_departement;COPY cog_departement FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_REGION}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_region;COPY cog_region FROM stdin WITH csv header delimiter ',';"
done

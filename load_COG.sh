#!/bin/bash

source config
cd $DATA_DIR
mkdir -p cog
cd cog
rm *.csv
wget -NS https://www.insee.fr/fr/statistiques/fichier/5057840/cog_ensemble_2021_csv.zip
unzip -o -j cog_ensemble_2021_csv.zip

CSV_COMMUNE=commune2021.csv
CSV_CANTON=canton2021.csv
CSV_ARRONDISSEMENT=arrondissement2021.csv
CSV_DEPARTEMENT=departement2021.csv
CSV_REGION=region2021.csv

for d in osm cadastre
do
  psql -d ${d} -U cadastre -f $BANO_DIR/sql/create_table_cog.sql
  cat ${CSV_COMMUNE}|       psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_commune;       COPY cog_commune FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_CANTON}|        psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_canton;        COPY cog_canton FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_ARRONDISSEMENT}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_arrondissement;COPY cog_arrondissement FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_DEPARTEMENT}|   psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_departement;   COPY cog_departement FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_REGION}|        psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_region;        COPY cog_region FROM stdin WITH csv header delimiter ',';"
done

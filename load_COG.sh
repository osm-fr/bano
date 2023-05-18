#!/bin/bash

set -e

source config
cd $DATA_DIR
mkdir -p cog
cd cog
rm -f *.csv
wget -NS https://www.insee.fr/fr/statistiques/fichier/6800675/cog_ensemble_2023_csv.zip
unzip -o -j cog_ensemble_2023_csv.zip

CSV_COMMUNE=v_commune_2023.csv
CSV_CANTON=v_canton_2023.csv
CSV_ARRONDISSEMENT=v_arrondissement_2023.csv
CSV_DEPARTEMENT=v_departement_2023.csv
CSV_REGION=v_region_2023.csv

for d in osm cadastre
do
  psql -d ${d} -U cadastre -f $BANO_DIR/sql/create_table_cog.sql
  cat ${CSV_COMMUNE}|       psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_commune;       COPY cog_commune FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_CANTON}|        psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_canton;        COPY cog_canton FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_ARRONDISSEMENT}|psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_arrondissement;COPY cog_arrondissement FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_DEPARTEMENT}|   psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_departement;   COPY cog_departement FROM stdin WITH csv header delimiter ',';"
  cat ${CSV_REGION}|        psql -d ${d} -U cadastre -c "TRUNCATE TABLE cog_region;        COPY cog_region FROM stdin WITH csv header delimiter ',';"
done

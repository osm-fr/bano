#!/bin/bash

set -e

source config
cd $DATA_DIR
mkdir -p cog
cd cog
rm -f *.csv
wget -NS https://www.insee.fr/fr/statistiques/fichier/5057840/cog_ensemble_2021_csv.zip
unzip -o -j cog_ensemble_2021_csv.zip

CSV_COMMUNE=commune2021.csv
CSV_CANTON=canton2021.csv
CSV_ARRONDISSEMENT=arrondissement2021.csv
CSV_DEPARTEMENT=departement2021.csv
CSV_REGION=region2021.csv

for psql in "$pgsql_CADASTRE" "$pgsql_OSM"
do
  $psql -f $BANO_DIR/sql/create_table_cog.sql
  cat "${CSV_COMMUNE}"        | $psql -c "TRUNCATE TABLE cog_commune;       COPY cog_commune FROM stdin WITH csv header delimiter ',';"
  cat "${CSV_CANTON}"         | $psql -c "TRUNCATE TABLE cog_canton;        COPY cog_canton FROM stdin WITH csv header delimiter ',';"
  cat "${CSV_ARRONDISSEMENT}" | $psql -c "TRUNCATE TABLE cog_arrondissement;COPY cog_arrondissement FROM stdin WITH csv header delimiter ',';"
  cat "${CSV_DEPARTEMENT}"    | $psql -c "TRUNCATE TABLE cog_departement;   COPY cog_departement FROM stdin WITH csv header delimiter ',';"
  cat "${CSV_REGION}"         | $psql -c "TRUNCATE TABLE cog_region;        COPY cog_region FROM stdin WITH csv header delimiter ',';"
done

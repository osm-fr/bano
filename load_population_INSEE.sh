#!/bin/bash

# Après téléchargement manuel d'un CSV à https://statistiques-locales.insee.fr/#c=indicator&i=pop_legales.popmun&s=2017&view=map1

CSV=/data/project/bano_data/insee/population_communale_2017.csv

for d in osm cadastre
do
  psql -d ${d} -U cadastre -v ON_ERROR_STOP=1 -f $BANO_DIR/sql/create_table_population_insee.sql
  cat ${CSV}| grep -v 'N/A'|psql -d ${d} -U cadastre -c "TRUNCATE TABLE population_insee;  COPY population_insee FROM stdin WITH csv delimiter ';';"
done

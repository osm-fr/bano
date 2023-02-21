#!/bin/bash

set -e

source config
cd $DATA_DIR
mkdir -p fantoir
cd fantoir
rm -rf FANTOIR* && rm -f *.zip
wget https://data.economie.gouv.fr/api/datasets/1.0/fichier-fantoir-des-voies-et-lieux-dits/attachments/fichier_national_fantoir_situation_janvier_2023_zip/ -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
$pgsql_OSM -f $BANO_DIR/sql/load_fantoir.sql
$pgsql_CADASTRE -f $BANO_DIR/sql/load_fantoir.sql

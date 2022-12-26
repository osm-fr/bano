#!/bin/bash

set -e

source config
cd $DATA_DIR
mkdir -p fantoir
cd fantoir
rm -rf FANTOIR* && rm -f *.zip
wget https://data.economie.gouv.fr/api/datasets/1.0/fichier-fantoir-des-voies-et-lieux-dits/attachments/fichier_national_fantoir_situation_novembre_2022_zip/ -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f $BANO_DIR/sql/load_fantoir.sql
psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -f $BANO_DIR/sql/load_fantoir.sql

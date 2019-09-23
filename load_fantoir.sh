#!/bin/bash

source config
cd $DATA_DIR
mkdir -p fantoir
cd fantoir
rm -rf FANTOIR* && rm *.zip
wget https://data.economie.gouv.fr/api/datasets/1.0/fichier-fantoir-des-voies-et-lieux-dits/attachments/fichier_national_fantoir_situation_juillet_2019_zip -O fantoir.zip
unzip fantoir.zip
mv FANTOIR* fantoir.txt
psql -d osm -U cadastre -f $BANO_DIR/sql/load_fantoir.sql

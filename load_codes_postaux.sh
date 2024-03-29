#!/bin/bash

set -e

source config
cd $DATA_DIR
mkdir -p codes_postaux
cd codes_postaux
rm -f *csv*
wget "https://datanova.legroupe.laposte.fr/explore/dataset/laposte_hexasmal/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&csv_separator=%3B" -O codes_postaux.csv
$pgsql_OSM -f $BANO_DIR/sql/create_and_load_codes_postaux.sql
$pgsql_CADASTRE -f $BANO_DIR/sql/create_and_load_codes_postaux.sql

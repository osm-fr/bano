#!/bin/bash

set -e

psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -c "
  DROP TABLE IF EXISTS export_csv CASCADE; \
  CREATE TABLE export_csv(
  id text,
  numero text,
  voie text,
  cp text,
  ville text,
  source text,
  lat decimal,
  lon decimal);"

for dep in `cat $BANO_DIR/deplist.txt`
do
  cat /data/sas_web/bano-${dep}.csv| psql -d cadastre -U cadastre -c "COPY export_csv FROM STDIN WITH CSV"
done

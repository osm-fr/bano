#!/bin/bash

set -e

$pgsql_CADASTRE -c "
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
  cat /data/sas_web/bano-${dep}.csv| $pgsql_CADASTRE -c "COPY export_csv FROM STDIN WITH CSV"
done

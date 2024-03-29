#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config

$pgsql_CADASTRE -c "DROP TABLE IF EXISTS export_csv CASCADE;
                                 CREATE TABLE export_csv(
                                 id text,
                                 numero text,
                                 voie text,
                                 cp text,
                                 ville text,
                                 source text,
                                 lat decimal,
                                 lon decimal);"

for dep in {01..19} 2A 2B {21..95} {971..974} 976
do
  cat /data/sas_web/bano-${dep}.csv| $pgsql_CADASTRE -c "COPY export_csv FROM STDIN WITH CSV"
done

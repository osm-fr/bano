#!/bin/bash

set -e

psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -f bano/sql/create_base.sql
psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -f sql/create_table_base_bano.sql
psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f bano/sql/create_base.sql
psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f sql/create_table_base_osm.sql

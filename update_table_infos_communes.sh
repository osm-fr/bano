#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

psql -d osm -U cadastre -f ./sql/update_table_infos_communes.sql


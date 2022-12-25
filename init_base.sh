#!/bin/bash

set -e

source config

$pgsql_CADASTRE -f bano/sql/create_base.sql
$pgsql_CADASTRE -f sql/create_table_base_bano.sql
$pgsql_OSM -f bano/sql/create_base.sql
$pgsql_OSM -f sql/create_table_base_osm.sql

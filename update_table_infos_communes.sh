#!/bin/bash

set -e

source config

$pgsql_OSM -f ./sql/update_table_infos_communes.sql

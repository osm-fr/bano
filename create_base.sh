#!/bin/bash

set -e

source config

createuser -s -d $POSTGRES_USER
createdb -E UTF-8 -T template0 -O $POSTGRES_USER $POSTGRES_DB_CADASTRE
createdb -E UTF-8 -T template0 -O $POSTGRES_USER $POSTGRES_DB_OSM

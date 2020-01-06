#!/bin/bash

psql -d osm -U cadastre -f sql/update_table_infos_communes.sql


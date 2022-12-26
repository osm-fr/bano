#!/bin/bash

set -e

python load_code_cadastre.py
psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -f sql/load_code_cadastre.sql

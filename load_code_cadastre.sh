#!/bin/bash

set -e

source config

python load_code_cadastre.py
$pgsql_CADASTRE -f bano/sql/load_code_cadastre.sql

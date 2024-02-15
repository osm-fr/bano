#!/bin/bash

set -e

psql -d bano -U cadastre -v ON_ERROR_STOP=1 -f bano/sql/create_base.sql

#!/bin/bash

set -e

psql -d bano -U cadastre -v ON_ERROR_STOP=1 -f sql/create_base.sql

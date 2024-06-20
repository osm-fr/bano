#!/bin/bash

set -e

psql -d cadastre -f stats.sql -v dept=$1

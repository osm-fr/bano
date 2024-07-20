#!/bin/bash

set -e

$pgsql_CADASTRE -f stats.sql -v dept=$1

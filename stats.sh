#!/bin/bash

set -e

source config

$pgsql_CADASTRE -f stats.sql -v dept=$1

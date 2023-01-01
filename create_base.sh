#!/bin/bash

set -e

createuser -s -d cadastre
createdb -E UTF-8 -T template0 -O cadastre bano

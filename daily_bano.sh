#!/bin/bash
./load_code_cadastre.sh
./import_echoues_france.py
./load_cumul.py france osm
./load_cumul.py france cadastre


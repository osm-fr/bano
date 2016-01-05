#!/bin/bash
./load_code_cadastre.sh
./import_echoues_france.py
./convert_qadastre_2_osm_differentiel.py
./import_parcelles_buildings_differentiel.py
cat deplist.txt | parallel -j 5 -l 8 export LANG=fr_FR.UTF-8\; python load_cumul.py {1} OSM > /dev/null
cat deplist.txt | parallel -j 5 -l 8 export LANG=fr_FR.UTF-8\; python load_cumul.py {1} CADASTRE > /dev/null
cat deplist.txt | parallel -j 5 -l 8 export LANG=fr_FR.UTF-8\; python load_cumul_place.py {1} > /dev/null
cd out
./banout-all.sh


#!/bin/bash

source /data/work/vdct/bano_venv37/bin/activate
cd /data/project/bano
source config

# Sources
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal CADASTRE {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal BAL {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_cadastre lieux_dits {1}
bano update_code_cadastre

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports
./copy_table_from_osm_to_cadastre.sh planet_osm_postal_code
./copy_table_from_osm_to_cadastre.sh planet_osm_communes_statut

# BANO
bano update_insee_lists
cat insee_cadastre.csv | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune CADASTRE --code_insee {1}
cat insee_osm.csv      | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM      --code_insee {1}
cat insee_locales.csv  | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL      --code_insee {1}
cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune_lieux-dits    --depts {1}

# exports
bano export

# ménage PostgreSQL
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_adresses;"
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_voies;"
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_places;"

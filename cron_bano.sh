#!/bin/bash

source /data/project/bano_v3/venv_v3/bin/activate

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

source config

./arborescence.sh

pip install -e .

# Sources
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano charge_ban {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano charge_ld_cadastre {1}

# bano update_bis_table
# ./copy_table_from_osm_to_cadastre.sh rep_b_as_bis


# BANO
# bano update_insee_lists
cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano rapprochement --dept {1}

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports

# psql -d osm -U cadastre -f sql/create_table_polygones_communes.sql
# psql -d osm -U cadastre -f sql/create_table_polygones_postaux.sql
# psql -d cadastre -U cadastre -f sql/post_copie_ban.sql

# exports
# cat deplist.txt | parallel -j 4 bano export {1}

# copie+zip dans le dossier web
# cat deplist.txt | parallel -j 4 bano publish {1}
# bano publish_aggregate

# ménage PostgreSQL
psql -d cadastre -U cadastre -c "VACUUM bano_adresses;"
psql -d cadastre -U cadastre -c "VACUUM bano_points_nommes;"
psql -d cadastre -U cadastre -c "VACUUM nom_fantoir;"
psql -d cadastre -U cadastre -c "GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO PUBLIC";
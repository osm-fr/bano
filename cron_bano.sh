#!/bin/bash

source $1

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

source config

./arborescence.sh

pip install -e .

# Sources
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal CADASTRE {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal BAL {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_ban {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_cadastre lieux_dits {1}
# bano update_code_cadastre
bano download_commune_summary
bano update_bis_table
bano remove_chars_in_ban
./copy_table_from_osm_to_cadastre.sh rep_b_as_bis


# BANO
# le dimanche, passe globale sur toutes les communes
# le reste de la semaine, ciblage des communes ayant eu des modifs dans OSM dans les dernières 24h
if [ `date +%u` -eq 7 ]
then
   bano update_insee_lists
   cat insee_locales.csv  | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL      --code_insee {1}
   cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAN           --depts {1}
   cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM           --depts {1}
   cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune_lieux-dits    --depts {1}
else
   bano update_insee_lists
   cat insee_locales.csv  | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL      --code_insee {1}
   cat insee_osm.csv      | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAN      --code_insee {1}
   cat insee_osm.csv      | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM      --code_insee {1}
   cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune_lieux-dits    --depts {1}
fi

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports
./copy_table_from_osm_to_cadastre.sh planet_osm_postal_code
./copy_table_from_osm_to_cadastre.sh infos_communes

psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f sql/create_table_polygones_communes.sql
./copy_table_from_osm_to_cadastre.sh polygones_insee
./copy_table_from_osm_to_cadastre.sh polygones_insee_geo

psql -d osm -U cadastre -v ON_ERROR_STOP=1 -f sql/create_table_polygones_postaux.sql
./copy_table_from_osm_to_cadastre.sh polygones_postaux
./copy_table_from_osm_to_cadastre.sh ban_odbl
psql -d cadastre -U cadastre -v ON_ERROR_STOP=1 -f sql/post_copie_ban_odbl.sql

# exports
cat deplist.txt | parallel -j 4 bano export {1}

# copie+zip dans le dossier web
cat deplist.txt | parallel -j 4 bano publish {1}
bano publish_aggregate

# ménage PostgreSQL
psql -d cadastre -U cadastre -c "VACUUM cumul_adresses;"
psql -d cadastre -U cadastre -c "VACUUM cumul_voies;"
psql -d cadastre -U cadastre -c "VACUUM cumul_places;"
psql -d cadastre -U cadastre -c "GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO PUBLIC";

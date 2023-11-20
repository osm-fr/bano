#!/bin/bash

source /data/project/bano_v3/venv_v3/bin/activate

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

echo 'debut du cron BANO' >> $SCRIPT_DIR/cron.log

source config

./arborescence.sh

pip install -e .

# Sources
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano charge_ban {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano charge_ld_cadastre {1}
bano update_bis_table

echo 'sources ok' >> $SCRIPT_DIR/cron.log

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports
bano update_table_communes
bano update_infos_communes

# psql -d osm -U cadastre -f sql/create_table_polygones_postaux.sql
# psql -d cadastre -U cadastre -f sql/post_copie_ban.sql
echo 'màj polygones ok' >> $SCRIPT_DIR/cron.log

# BANO
cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano rapprochement --dept {1}

echo 'rapprochement ok' >> $SCRIPT_DIR/cron.log

# exports
# cat deplist.txt | parallel -j 4 bano export {1}

# copie+zip dans le dossier web
# cat deplist.txt | parallel -j 4 bano publish {1}
# bano publish_aggregate

# ménage PostgreSQL
psql -d bano -U cadastre -c "VACUUM bano_adresses;"
psql -d bano -U cadastre -c "VACUUM bano_points_nommes;"
psql -d bano -U cadastre -c "VACUUM nom_fantoir;"
psql -d bano -U cadastre -c "GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO PUBLIC";
echo 'fin du cron BANO' >> $SCRIPT_DIR/cron.log

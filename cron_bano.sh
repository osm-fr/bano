#!/bin/bash

set -e

source /data/project/bano_v3/venv_v3/bin/activate

echo 'debut du cron BANO'

source config

./arborescence.sh

pip install -e .

# Sources
cat deplist.txt | parallel -j 4 export LANG=$LANG\; bano charge_ban {1}
cat deplist.txt | parallel -j 4 export LANG=$LANG\; bano charge_ld_cadastre {1}
bano update_bis_table

echo 'sources ok'

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports
bano update_table_communes
bano update_infos_communes

# $pgsql_BANO -f sql/create_table_polygones_postaux.sql
# $pgsql_CADASTRE -f sql/post_copie_ban.sql
echo 'màj polygones ok'

# BANO
cat deplist.txt        | parallel -j 4 export LANG=$LANG\; bano rapprochement --dept {1}

echo 'rapprochement ok'

echo 'preparation export'
bano prepare_export
echo 'preparation export finie'

# exports
echo 'export'
cat deplist.txt | parallel -j 4 bano export {1}
echo 'export fini'

# copie+zip dans le dossier web
cat deplist.txt | parallel -j 4 bano publish {1}
bano publish_aggregate

# ménage PostgreSQL
$pgsql_BANO -c "VACUUM bano_adresses;"
$pgsql_BANO -c "VACUUM bano_points_nommes;"
$pgsql_BANO -c "VACUUM nom_fantoir;"
$pgsql_BANO -c "GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO PUBLIC";
echo 'fin du cron BANO'

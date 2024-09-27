#!/bin/bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

echo 'debut du cron BANO' >> $SCRIPT_DIR/cron.log

source config

./arborescence.sh

pip install -e .

# Sources
cat deplist.txt | parallel -j $PARALLEL_JOBS export LANG=$LANG\; bano charge_ban {1}
cat deplist.txt | parallel -j $PARALLEL_JOBS export LANG=$LANG\; bano charge_ld_cadastre {1}
bano update_bis_table

echo 'sources ok' >> $SCRIPT_DIR/cron.log

# Mise à jour quotidienne dans la base cadastre des couches des polygones postaux d'OSM et des statuts admin de communes en vue des exports
bano update_table_communes
bano update_infos_communes

# $pgsql_BANO -f sql/create_table_polygones_postaux.sql
# $pgsql_CADASTRE -f sql/post_copie_ban.sql
echo 'màj polygones ok' >> $SCRIPT_DIR/cron.log

# BANO
cat deplist.txt        | parallel -j $PARALLEL_JOBS export LANG=$LANG\; bano rapprochement --dept {1}

echo 'rapprochement ok' >> $SCRIPT_DIR/cron.log

echo 'preparation export' >> $SCRIPT_DIR/cron.log
bano prepare_export
echo 'preparation export finie' >> $SCRIPT_DIR/cron.log

# exports
echo 'export' >> $SCRIPT_DIR/cron.log
cat deplist.txt | parallel -j $PARALLEL_JOBS bano export {1}
echo 'export fini' >> $SCRIPT_DIR/cron.log

# copie+zip dans le dossier web
cat deplist.txt | parallel -j $PARALLEL_JOBS bano publish {1}
bano publish_aggregate

# ménage PostgreSQL
$pgsql_BANO -c "VACUUM bano_adresses;"
$pgsql_BANO -c "VACUUM bano_points_nommes;"
$pgsql_BANO -c "VACUUM nom_fantoir;"
$pgsql_BANO -c "GRANT SELECT ON ALL TABLES IN SCHEMA PUBLIC TO PUBLIC";

# Pifometre - croiement voies & limites admin
cat deplist.txt | parallel -j $PARALLEL_JOBS export LANG=$LANG\; bano croisement_voies_limites {1}

echo 'fin du cron BANO' >> $SCRIPT_DIR/cron.log

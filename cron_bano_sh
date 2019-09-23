#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
source $SCRIPT_DIR/config
source /data/work/vdct/bano_venv/bin/activate

echo `date` > $SCRIPT_DIR/cron.log
echo debut >> $SCRIPT_DIR/cron.log
 
cd /data/download
#rm -rf france_metro_dom_com_nc.osm.pbf
wget -NS http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf

cd $BANO_DIR

/app/imposm/imposm import -mapping bano.yml -read /data/download/france_metro_dom_com_nc.osm.pbf -overwritecache -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff
/app/imposm/imposm import -mapping bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff

psql -d osm -U cadastre -f sql/finalisation.sql

./load_code_cadastre.sh
cat deplist.txt | parallel -j 5 export LANG=fr_FR.UTF-8\; python load_cumul.py {1} OSM #> /dev/null
cat deplist.txt | parallel -j 5 export LANG=fr_FR.UTF-8\; python load_cumul.py {1} CADASTRE #> /dev/null
cat deplist.txt | parallel -j 5 export LANG=fr_FR.UTF-8\; python load_cumul.py {1} BAL #> /dev/null
cat deplist.txt | parallel -j 5 export LANG=fr_FR.UTF-8\; python load_cumul_place.py {1} #> /dev/null

echo `date` >> $SCRIPT_DIR/cron.log
echo fin >> $SCRIPT_DIR/cron.log

# /app/imposm/imposm diff -mapping /home/vdechateauthierry/bano/bano.yml -cachedir /data/bano_imposm_cache -dbschema-production public -diffdir /data/bano_imposm_diff -connection 'postgis://cadastre@localhost/osm'?prefix=NONE /data/bano_imposm_diff/diff_france_metro_dom_com_nc.osc.gz
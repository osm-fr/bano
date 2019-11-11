#!/bin/bash

source /data/work/vdct/bano_venv37/bin/activate
cd /data/project/bano
source config
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal CADASTRE {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal BAL {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_cadastre lieux_dits {1}
bano update_code_cadastre
bano update_insee_lists
# psql -d osm -U cadastre -A -c "SELECT distinct commune_code FROM bal_cadastre ORDER BY 1" |tail -n +2|grep -v ')' > insee_bal_cadastre.csv;
# psql -d osm -U cadastre -A -c "SELECT distinct commune_code FROM bal_locales ORDER BY 1" |tail -n +2|grep -v ')' > insee_bal_locales.csv;
cat insee_cadastre.csv | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune CADASTRE --code_insee {1}
cat insee_osm.csv      | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM      --code_insee {1}
cat insee_locales.csv  | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL      --code_insee {1}
cat deplist.txt        | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune_lieux-dits    --depts {1}
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_adresses;"
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_voies;"
psql -d cadastre -U cadastre -c "VACUUM FULL cumul_places;"

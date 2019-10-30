#!/bin/bash

source /data/work/vdct/bano_venv37/bin/activate
cd /data/project/bano
source config
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal CADASTRE {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal BAL {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_cadastre lieux_dits {1}
bano update_code_cadastre
psql -d osm -U cadastre -A -c "SELECT distinct commune_code FROM bal_cadastre ORDER BY 1" |tail -n +2|grep -v ')' > insee_bal_cadastre.csv;
cat insee_bal_cadastre.csv | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune CADASTRE --code_insee {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM --depts {1}
psql -d osm -U cadastre -A -c "SELECT distinct commune_code FROM bal_locales ORDER BY 1" |tail -n +2|grep -v ')' > insee_bal_locales.csv;
cat insee_bal_locales.csv | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL --code_insee {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune_lieux-dits --depts {1}

# chargement BAL/CADASTRE : si chargement effectif, noter le departement pour màj. Idem lieux-dits
# tuiles OSM : liste des INSEE des communes concernées
#  le cron passe sur la liste dedoublonnée des INSEE des chrgements et des tuiles
# au début du cron, initialiser les fichiers de listes INSEE pour chaque source
#  dans le cron, alimenter ces fichiers si chargement
#  à la fin, fabriquer les listes dedoublonnées pour le cron
# pour les tuiles : commencer à 00:00, avec l'agregat des fichiers tiles de la veille
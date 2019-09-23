#!/bin/bash

source /data/work/vdct/bano_venv37/bin/activate
cd /data/project/bano
source config
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal CADASTRE {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano download_bal BAL {1}
bano update_code_cadastre
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune CADASTRE --depts {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune CADASTRE --depts {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune OSM --depts {1}
cat deplist.txt | parallel -j 4 export LANG=fr_FR.UTF-8\; bano process_commune BAL --depts {1}

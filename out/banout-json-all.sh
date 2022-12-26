#!/bin/bash

set -e

# script écrit et maintenu par cquest@openstreetmap.fr

# export multi-thread de cumul_voie + cumul_adresse + cumul_place en json
parallel -j 8 sh banout-json.sh -- 01 02 03 04 05 06 07 08 09 `seq 10 19` 2A 2B `seq 21 95` `seq 971 974` 976

# fusion en un fichier unique
rm -f full.sjson*
for dep in {01..19} 2A 2B {21..95} {971..974} 976 ; do grep -v ^$ bano-$dep.json | gzip -9 >> full.sjson.gz ; gzip -9 bano-$dep.json ; done

# compression et copie sur le site web
sudo mv *json.gz /data/project/bano.openstreetmap.fr/web/data/

# ménage final
rm bano-*.json

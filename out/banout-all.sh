#!/bin/bash
parallel -j 8 sh banout.sh > /dev/null -- 01 02 03 04 05 06 07 08 09 `seq 10 19` 2A 2B `seq 21 95` `seq 971 974` 976

# fichier global France
for d in 01 02 03 04 05 06 07 08 09 `seq 10 19` 2A 2B `seq 21 95` `seq 971 974` 976; do cat /data/project/bano.openstreetmap.fr/web/data/bano-$d.csv >> full.csv ; done
gzip -9 full.csv
mv full.csv.gz /data/project/bano.openstreetmap.fr/web/data/


#!/bin/bash

# script écrit et maintenu par cquest@openstreetmap.fr

# export multi-thread de cumul_voie + cumul_adresse + cumul_place en json
parallel -j 8 sh banout-json.sh -- 01 02 03 04 05 06 07 08 09 `seq 10 19` 2A 2B `seq 21 95` `seq 971 974`

# export des communes > json
psql cadastre -t -A -c " \
SELECT '{\"id\": \"' || insee || '\",\"type\": \"' || CASE WHEN population<1 THEN 'village' WHEN population<'10' THEN 'town' ELSE 'city' END  || '\",\"name\": \"' || g.nom || '\",\"postcode\": \"' || ca.code_postal || '\",\"lat\": \"' || round(lat_chf,6) || '\",\"lon\": \"' || round(lon_chf,6) || '\",\"city\": \"' || g.nom|| '\",\"departement\": \"' || cog.nom_dep || '\", \"region\": \"' || cog.nom_reg || '\", \"population\": ' || population || ', \"adm_weight\": ' || CASE WHEN statut LIKE 'Capital%' THEN 6 WHEN statut = 'Préfecture de régi' THEN 5 WHEN statut='Préfecture' THEN 4 WHEN statut LIKE 'Sous-pr%' THEN 3 WHEN statut='Chef-lieu canton' THEN 2 ELSE 1 END || ', \"importance\": ' || greatest(0.075,round(log((CASE WHEN statut LIKE 'Capital%' THEN 6 WHEN statut = 'Préfecture de régi' THEN 5 WHEN statut='Préfecture' THEN 4 WHEN statut LIKE 'Sous-pr%' THEN 3 WHEN statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(population+1)/3),4)) || '}' \
FROM geofla_plus g join code_cadastre ca on (ca.insee_com=insee) join (select dep, nom_dep, nom_reg from cog group by dep,nom_dep, nom_reg) as cog on (cog.dep=left(insee,2) or cog.dep=left(insee,3)) order by insee; \
" | grep id > full.sjson

# fusion en un fichier unique
for dep in {01..19} 2A 2B {21..95} {971..974} ; do grep -v ^$ tmp-$dep-full.json >> full.sjson ; done

# compression et copie sur le site web
gzip full.sjson
sudo mv full.sjson.gz /data/project/bano.openstreetmap.fr/web/data/

# ménage final
rm tmp-*-full.json

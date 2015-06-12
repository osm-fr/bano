## http://opendata.montpelliernumerique.fr/Point-adresse

cd 034_montpellier
rm -rf VilleMTP*

wget http://opendata.montpelliernumerique.fr/datastore/VilleMTP_MTP_PointAdresse.zip
unzip -o VilleMTP_MTP_PointAdresse.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/VilleMTP_MTP_PointAdresse.shp -overwrite -nlt GEOMETRY -nln import_montpellier

wget http://opendata.montpelliernumerique.fr/datastore/VilleMTP_MTP_FilaireVoies.zip
unzip -o VilleMTP_MTP_FilaireVoies.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/VilleMTP_MTP_FilaireVoies.shp  -overwrite -nlt GEOMETRY -nln import_montpellier_voies

# remise en forme code fantoir du fichier voies
psql cadastre -c "update import_montpellier_voies set rivoli_dgi=substr(rivoli_dgi,2,4) where rivoli_dgi ~ '^0[0-9BX][0-9]{3}';"
psql cadastre -c" update import_montpellier_voies set rivoli_dgi=left(rivoli_dgi,4) where rivoli_dgi ~ '^[0-9BX]{4} ?[A-Z]$';"

psql cadastre -c "delete from cumul_adresses where source = 'OD-MONTPELLIER';"
psql cadastre -c "insert into cumul_adresses (select wkb_geometry, num_suf, lib_off, lib_off,'34172' || rivoli_dgi || cle_rivoli,'34172',null,'034',null,'OD-MONTPELLIER',null, null from (select code_voie, rivoli_dgi, cle_rivoli from import_montpellier_voies join fantoir_voie on (code_insee='34172' and id_voie=rivoli_dgi) group by code_voie, rivoli_dgi, cle_rivoli) as r, import_montpellier a where num_suf !='0' and a.code_voie=r.code_voie);"


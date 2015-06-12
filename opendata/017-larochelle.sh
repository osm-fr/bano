cd 017_larochelle

# ménage initial
rm -f voirie*

# download
wget http://www.opendata.larochelle.fr/telechargement/shape/voieadresse/voirie_filaire_numero_wgs84_shp.zip
wget http://www.opendata.larochelle.fr/telechargement/shape/voieadresse/voirie_filaire_troncon_wgs84_shp.zip
wget http://www.opendata.larochelle.fr/telechargement/shape/voieadresse/voirie_filaire_voie_wgs84_shp.zip
wget http://www.opendata.larochelle.fr/telechargement/csv/H_referentiel_geographique/voieadresse/voirie_filaire_indice.csv

# uppression lignes vides dans voirie_filaire_indice.csv
grep -v ^$ voirie_filaire_indice.csv > indice.csv

# unzip
unzip voirie_filaire_numero_wgs84_shp.zip
unzip voirie_filaire_troncon_wgs84_shp.zip
unzip voirie_filaire_voie_wgs84_shp.zip

# import potgres
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre voirie_filaire_numero_wgs84.shp  -overwrite -nlt GEOMETRY -nln import_rochelle_numero
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre voirie_filaire_troncon_wgs84.shp  -overwrite -nlt GEOMETRY -nln import_rochelle_troncon
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre voirie_filaire_voie_wgs84.shp  -overwrite -nlt GEOMETRY -nln import_rochelle_voie
psql cadastre -c "create table if not exists import_rochelle_indices (ind_id text, ind_libelle text); truncate import_rochelle_indices;"
psql cadastre -c "\copy import_rochelle_indices from 'indice.csv' with (format csv, delimiter ';', header true);"

psql cadastre -c "delete from cumul_adresses where source='OD-LAROCHELLE';"
psql cadastre -c "insert into cumul_adresses (select n.wkb_geometry as geometrie, trim(numero_val::text || ' ' || coalesce(ind_libelle,'')) as numero, v.voie_libel as voie_cadastre, NULL as voie_osm, '17300' || f.id_voie || f.cle_rivoli as fantoir, '17300' as insee_com,NULL as cadastre_com,'017' as dept, '' as code_postal, 'OD-LAROCHELLE' as source,null, trim(f.nature_voie || ' ' || f.libelle_voie) as voie_fantoir from import_rochelle_numero n join import_rochelle_indices i on (i.ind_id::numeric=n.numero_ind) join import_rochelle_troncon t on (t.troncon_id=n.numero_tro) join import_rochelle_voie v on (v.voie_id=t.troncon_vo) join fantoir_voie f on (f.code_insee='17300' and f.id_voie=v.voie_fanto));"

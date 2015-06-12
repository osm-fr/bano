cd 035_rennes
rm -rf voies_adresses*
# récupération des shapefile contenant les points adresse
wget http://www.data.rennes-metropole.fr/fileadmin/user_upload/data/data_sig/referentiels/voies_adresses/voies_adresses_shp_wgs84.zip
unzip -o voies_adresses_shp_wgs84.zip
# import dans postGIS
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/voies_adresses_shp_wgs84/donnees/rva_adresses.shp  -overwrite -nlt GEOMETRY -nln import_rennes_addr
# récupération des csv pour le lien avec FANTOIR (pas dispo dans les shapefile)
wget http://www.data.rennes-metropole.fr/fileadmin/user_upload/data/data_sig/referentiels/voies_adresses/voies_adresses_csv.zip
unzip -o voies_adresses_csv.zip
# import dans postgres
psql cadastre -c "create table IF NOT EXISTS import_rennes_voies (code_insee text, id_voie numeric, fantoir text, type text, voie_nom text, voie_nom_complet text, article1 text, prenom1 text, article2 text, prenom2 text, particule text, nom text);TRUNCATE TABLE import_rennes_voies;"
psql cadastre -c "\\copy import_rennes_voies from '/tmp/voies_adresses_csv/donnees/rva_voies.csv' with DELIMITER AS ';' csv header;"
# création des adresses dans cumul_adresses avec données FANTOIR
psql cadastre -c "begin; delete from cumul_adresses where source='OD-RENNES'; insert into cumul_adresses (select wkb_geometry, numero || coalesce(extension,'') || (case when batiment is null then '' else ' '|| batiment end), a.voie_nom, a.voie_nom, concat(a.code_insee,f.id_voie,f.cle_rivoli), a.code_insee, null, '035', null, 'OD-RENNES', null from import_rennes a join import_rennes_voies v on (a.id_voie=v.id_voie) join fantoir_voie f on (f.code_insee=a.code_insee and f.id_voie=v.fantoir)); COMMIT;"

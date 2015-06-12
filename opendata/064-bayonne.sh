cd 064_bayonne
rm -rf adresse_bayonne*

wget http://www.bayonne.fr/fileadmin/user_upload/fichiers/Mairie_de_Bayonne/La_Mairie/Repertoire_donnees_publiques/adresse.zip
unzip -qj adresse.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre adresse_bayonne.shp -overwrite -nlt GEOMETRY -nln import_bayonne
psql cadastre -c "delete from cumul_adresses where source='OD-BAYONNE'; insert into cumul_adresses (select wkb_geometry, numero, voie as voie_cadastre, case when voie_osm !='' then voie_osm else voie_cadastre end as voie_osm, code_insee||rivoli||cle_rivoli as fantoir, code_insee as insee_com, null, '064' as dept, code_post as code_postal, 'OD-BAYONNE' as source, null, null from import_bayonne b left join cumul_voies v on (fantoir=code_insee||rivoli||cle_rivoli));"


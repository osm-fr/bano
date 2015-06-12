cd 086_poitiers

# fichier litéral des adresses
curl 'https://sig.grandpoitiers.fr/imagettes_geoportal/MetadoImagettes/table_ADRESSES.csv' | iconv -f iso-8859-1 -t utf8 table_ADRESSES.csv > table_ADRESSES.csv

psql cadastre -c "drop table if exists import_poitiers; create table import_poitiers_voies (id1 text, id2 text, numero text, rivoli text, typeadr text, statutadr text, libelle text, nom text, commune text);"
psql cadastre -c "\copy import_poitiers_voies from 'table_ADRESSES_utf8.csv' with (format csv, header true, delimiter ';');"

# fichier contenant les géométries
curl 'http://inspire.sgmap.fr/api/datasets/54e30714410fc47e759a3c82/resources/54e30714410fc47e759a3c86/download?format=SHP&projection=Lambert93' > grd-poitiers.zip
unzip grd-poitiers.zip

# import dans postGIS
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre Geoportail_WMS_PreviewAdresses.shp -overwrite -nlt GEOMETRY -nln import_poitiers_adr

psql cadastre -c "alter table import_poitiers_adr drop column ogc_fid;"

# création des adresses dans cumul_adresses
psql cadastre -c "
begin;
delete from cumul_adresses where source='OD-POITIERS';
insert into cumul_adresses select wkb_geometry, trim(numero), nom, coalesce(voie_osm, voie_cadastre), '86194'||rivoli, '86194',null,'086',null,'OD-POITIERS',null,null from import_poitiers_voies v join import_poitiers_adr a on (a.identifian=v.id2::numeric) left join cumul_voies c on (c.fantoir='86194'||rivoli) order by rivoli, numero;
COMMIT;
"


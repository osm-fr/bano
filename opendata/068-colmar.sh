## http://www.agglo-colmar.fr/geo

cd 068_colmar
wget http://sig.agglo-colmar.fr/web/Sig/OpenData/FR-246800726-678/FR-246800726-678.zip
unzip FR-246800726-678.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre FR_246800726_678.shp -overwrite -nlt GEOMETRY -nln import_colmar
psql cadastre -c "
BEGIN;
DELETE FROM cumul_adresses WHERE source='OD-COLMAR';
INSERT INTO cumul_adresses (SELECT wkb_geometry, numero, voie, null, null, null, com_insee_, null, '068', null, 'OD-COLMAR',null from import_colmar);
COMMIT;
"

cd 031_toulouse
curl "https://data.toulouse-metropole.fr/explore/dataset/numero-de-rue/download/?format=geojson&timezone=Europe/Berlin" > num.geojson
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre num.geojson -overwrite -nlt GEOMETRY -nln import_toulouse
psql cadastre -c "
BEGIN;
DELETE FROM cumul_adresses WHERE source='OD-TOULOUSE';
INSERT INTO cumul_adresses (SELECT wkb_geometry, trim(numero||' '||coalesce(repetition,'')), libelle, null,concat(substr(sti,1,5),substr(rivoli,7,5)), substr(sti,1,5), null, '031', null, 'OD-TOULOUSE',null,null from import_toulouse);
COMMIT;
"


## http://www.mulhouse.fr/fr/Localisation-et-caracteristiques-des-adresses-postales/Localisation-et-caracteristiques-des-adresses-postales.html

cd 068_mulhouse
wget http://www.mulhouse.fr/medias/mairie/open-data/Donnees/RGU/SHAPE_L93/RGU_ADRESSE_POSTALE_L93.zip
unzip RGU_ADRESSE_POSTALE_L93.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre RGU_ADRESSE_POSTALE_L93.shp  -overwrite -nlt GEOMETRY -nln import_mulhouse
psql cadastre -c "
BEGIN;
DELETE FROM cumul_adresses WHERE source='OD-MULHOUSE';
INSERT INTO cumul_adresses (SELECT wkb_geometry, substr(adresse_co,1,strpos(adresse_co,' ')-1), substr(adresse_co,strpos(adresse_co,' ')+1), null, substr(com_num::text,1,5), null, null, '068', codepostal, 'OD-MULHOUSE',null,null from import_mulhouse);
COMMIT;
"


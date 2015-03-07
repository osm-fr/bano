cd /tmp
rm -rf BMO_BaseAdresses*

# récupération des shapefile contenant les points adresse
wget https://geo.pays-de-brest.fr/donnees/Documents/Public/BMO_BaseAdresses.zip
unzip -o BMO_BaseAdresses.zip

# import dans postGIS
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre BMO_BaseAdresses/BMO_BaseAdresses/adre_p.shp -overwrite -nlt GEOMETRY -nln import_brest

# création des adresses dans cumul_adresses avec données FANTOIR
psql cadastre -c "begin; delete from cumul_adresses where source='OD-BREST'; insert into cumul_adresses (select wkb_geometry as geometrie, trim(noimm || ' ' || lsiim) as numero, libru as voie_cadastre, nmvoi as voie_osm, idrue||f.cle_rivoli as fantoir, depco as insee_com, '', '029', null,'OD-BREST',null,'' from import_brest join fantoir_voie f on (f.code_insee=depco and f.id_voie=codru)); COMMIT;"

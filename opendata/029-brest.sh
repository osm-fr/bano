cd 029_brest
rm -rf REF_VOI*

wget "https://applications002.brest-metropole.fr/VIPDU72/GPB/REF_VOI_ADRESSES_V.zip"
unzip -o REF_VOI_ADRESSES_V.zip

# import dans postGIS
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre REF_VOI_ADRESSES_V.shp -overwrite -nlt GEOMETRY -nln import_brest

# création des adresses dans cumul_adresses avec données FANTOIR
psql cadastre -c "
begin;
delete from cumul_adresses where source='OD-BREST';
insert into cumul_adresses (select wkb_geometry as geometrie, trim(noimm || ' ' || coalesce(lsiim,'')) as numero, libru as voie_cadastre, libru as voie_osm, idrue||f.cle_rivoli as fantoir, depco as insee_com, '', '029', null,'OD-BREST',null,'' from import_brest join fantoir_voie f on (f.code_insee=depco and f.id_voie=codru));
COMMIT;
"

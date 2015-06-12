cd 006_cannes
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre adr_nvoi.shp  -overwrite -nlt GEOMETRY -nln import_cannes
psql cadastre -c "
insert into cumul_adresses (select wkb_geometry,numero, adr_ok, trim(substr(adrminus,length(numero)+1)),v.fantoir,codinsee,null,'006',cod_post,'OD-CANNES',null,null from import_cannes left join cumul_voies v on (v.insee_com=codinsee and v.voie_osm=trim(substr(adrminus,length(numero)+1))));
"


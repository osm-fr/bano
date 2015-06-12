# conversion geojson en csv
cd 038_grenoble
echo 'longitude,latitude,numero,voie,cp' > VilleDeGrenoble-OSM.csv
cat VilleDeGrenoble-OSM.json | sed 's/"type":"MultiPoint","coordinates":\[\[\([0-9\.,]*\).*\]\]/"type":"Point","coordinates":\[\1\]/' | grep Point | sed 's/^.*"coordinates":\[\(.*\)\].*"ADRES_LIBEL":"\(.*\)","VOIE_NOMCOMPL":"\(.*\)","ADRES_CODEPOST":\([0-9]*\).*$/\1,\2,\3,\4/' >> VilleDeGrenoble-OSM.csv
# import dans postgres
psql cadastre -c "create table if not exists import_grenoble (lon float, lat float, numero text, voie text, cp text); truncate import_grenoble;"
psql cadastre -c "\copy import_grenoble from VilleDeGrenoble-OSM.csv with csv;"
# mise à jour de cumul_adresses
psql cadastre -c "delete from cumul_adresses where source = 'OD-GRENOBLE';"
psql cadastre -c "insert into cumul_adresses select st_setsrid(st_point(lon,lat),4326),numero, null, voie, null, '38185', null, '038',cp,'OD-GRENOBLE',null,null from import_grenoble;"
# mise à jour du code fantoir par comparaison avec cumul_voies
psql cadastre -c "with u as (select a.voie_osm as a_nom, v.fantoir as v_fantoir from cumul_adresses a left join cumul_voies v on ((lower(replace(v.voie_osm,'-',' '))=lower(replace(a.voie_osm,'-',' ')) or lower(replace(v.voie_cadastre,'-',' '))=lower(replace(a.voie_osm,'-',' '))) and v.insee_com=a.insee_com) where a.source='OD-GRENOBLE' and v.fantoir is not null group by 1,2) update cumul_adresses set fantoir=v_fantoir from u where voie_osm=a_nom and source='OD-GRENOBLE';"


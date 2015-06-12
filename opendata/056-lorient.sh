## http://geobretagne.fr/geonetwork/apps/georchestra/?uuid=urn:isogeo:metadata:uuid:8b7128bd-3fa8-487a-9773-d95bd0cfa579

cd 056_lorient
curl http://geoservices.lorient-agglo.fr/documents/ref_voirie/adresses/shapefile/cc48/la/adresses.zip > 056-lorient-adresses.zip
unzip -o 056-lorient-adresses.zip

export SHAPE_ENCODING="ISO-8859-1"
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre adresses.shp -overwrite -nlt GEOMETRY -nln import_lorient

psql cadastre -c "
delete from cumul_adresses where source='OD-LORIENT'; 
insert into cumul_adresses select st_centroid(wkb_geometry), trim(adress_num||' '||adr_except), nom_voie, null, insee||fantoir||cle_rivoli, insee, null, '056', null, 'OD-LORIENT', null from import_lorient left join fantoir_voie f on (f.code_insee=insee and f.id_voie=fantoir);

-- mise à jour des noms de voie depuis cumul_voies
with u as (select a.fantoir as u_fantoir, v.voie_osm as u_nom from cumul_adresses a join cumul_voies v on (v.fantoir=a.fantoir) where a.source='OD-LORIENT' and v.voie_osm != '' group by 1,2) update cumul_adresses set voie_osm=u_nom from u where source='OD-LORIENT' and fantoir=u_fantoir;
"
export SHAPE_ENCODING="UTF-8"

cd /tmp
rm -rf FV*

curl -o cub-numeros.zip 'http://data.bordeaux-metropole.fr/files.php?gid=20&format=2'
unzip -o cub-numeros.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/FV_NUMVO_P.shp -overwrite -nlt GEOMETRY -nln import_cub

curl -o cub-denomination-voies.zip 'http://data.bordeaux-metropole.fr/files.php?gid=23&format=1'
unzip -o cub-denomination-voies.zip
ogr2ogr  -f PostgreSQL PG:dbname=cadastre /tmp/FV_VOIE_A.shp  -overwrite -nlt GEOMETRY -nln import_cub_voie_a

psql cadastre -c "delete from cumul_adresses where source='OD-CUB';"
psql cadastre -c "insert into cumul_adresses select a.wkb_geometry, a.numero, d.nomng, d.nomng, case when d.coderiv is null or length(d.coderiv)>5 then null else concat('33',c.ident,d.coderiv) end as fantoir, concat('33',c.ident) as insee, null,'033',null,'OD-CUB',null from import_cub a join import_cub_voie_a d on (d.gid=a.rs_fv_voie) join import_cub_comm c on (c.gid=d.rhfv_commu);"
psql cadastre -c "with u as (select voie_cadastre as voie_m, insee_com as insee_m, fantoir_o from cumul_adresses m join (select insee_com as insee_o, fantoir as fantoir_o, voie_osm as voie_o from cumul_adresses where fantoir like '33%' and voie_osm is not null group by fantoir, voie_osm, insee_com) as o on (voie_o=voie_cadastre and insee_o=insee_com) where source='OD-CUB' and fantoir is null group by voie_cadastre, insee_com, fantoir_o) update cumul_adresses set fantoir=fantoir_o from u where insee_com=insee_m and voie_cadastre=voie_m and source='OD-CUB' and fantoir is null;"




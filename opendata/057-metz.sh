cd 057_metz
curl -k -o metz-numero.zip 'https://geo-ws.metzmetropole.fr/geoserver/ows?service=WFS&version=2.0.0&request=GetFeature&typeName=fdp_voi_nume&srsName=EPSG:4326&outputFormat=SHAPE-ZIP'
unzip metz-numero.zip
unzip metz-voie.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre fdp_voi_nume.shp -overwrite -nlt GEOMETRY -nln import_metz_numero
psql cadastre -c "truncate table import_metz_numero; alter table import_metz_numero alter COLUMN the_orient type numeric(10,2); alter table import_metz_numero alter COLUMN the_orien0 type numeric(10,2);"
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre fdp_voi_nume.shp -append -nlt GEOMETRY -nln import_metz_numero
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre fdp_voi_voie.shp -overwrite -nlt GEOMETRY -nln import_metz_voie
psql cadastre -c "begin; delete from cumul_adresses where source='OD-METZ'; insert into cumul_adresses (select n.wkb_geometry, n.lib, replace(regexp_replace(replace(concat(v.typ,' ',v.exc,' ',v.lib),'  ',' '),'^ ',''),E'\x27 ',E'\x27'), null, concat(n._voie,v.cle), n._commid, '', '057', '', 'OD-METZ', 0,'' from import_metz_numero n join import_metz_voie v on (v.id=n._voie)); commit;"
cd -


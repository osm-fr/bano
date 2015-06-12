cd 00_osm
wget -nc http://osm13.openstreetmap.fr/~cquest/openfla/export/communes-plus-20140630-100m-shp.zip
unzip -o communes-plus-20140630-100m-shp.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre communes-plus-20140630-100m-shp/communes-plus-20140630-100m.shp -overwrite -nlt GEOMETRY -nln geofla_plus
psql cadastre -c "alter table geofla_plus alter surf_m2 type numeric(24,0); truncate geofla_plus;"
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre communes-plus-20140630-100m-shp/communes-plus-20140630-100m.shp -append -nlt GEOMETRY -nln geofla_plus
psql cadastre -c "alter table geofla_plus add column lat_chf numeric; alter table geofla_plus add column lon_chf numeric;"
psql cadastre -c "update geofla_plus set lat_chf=st_y(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2154),4326)), lon_chf=st_x(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2154),4326));"
psql cadastre -c "update geofla_plus set lat_chf=st_y(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2975),4326)), lon_chf=st_x(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2975),4326)) where insee like '974%';"
psql cadastre -c "update geofla_plus set lat_chf=st_y(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),32620),4326)), lon_chf=st_x(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),32620),4326)) where insee like '971%' or insee like '972%';"
psql cadastre -c "update geofla_plus set lat_chf=st_y(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2972),4326)), lon_chf=st_x(st_transform(st_setsrid(st_point(x_chf_lieu*100,y_chf_lieu*100),2972),4326)) where insee like '973%';"


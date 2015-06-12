cd 029_concarneau
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre point_adresse_cca_21052014.shp -overwrite -nlt GEOMETRY -nln import_concerneau
psql cadastre -c "insert into cumul_adresses select wkb_geometry, numero, nomvoie, null, null, insee, null, '029',null,'OD-CONCARNEAU',null, null from import_concarneau;"


cd /home/cquest/adresses_manosque/
ogr2ogr -s_srs EPSG:2154 -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre pointadresse_04112_L93.shp -overwrite -nlt GEOMETRY -nln import_manosque
cd -


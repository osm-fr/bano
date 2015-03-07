## http://data.nantes.fr/donnees/detail/adresses-postales-de-nantes-metropole-par-commune/

cd /tmp
rm -rf *ADRESSES_NM*

wget http://data.nantes.fr/fileadmin/data/datastore/nm/urbanisme/24440040400129_NM_NM_00001/ADRESSES_NM_shp_l93.zip
unzip ADRESSES_NM_shp_l93.zip
export SHAPE_ENCODING="ISO-8859-1"
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/ADRESSES_NM.shp -overwrite -nlt GEOMETRY -nln import_nantes
psql cadastre -c "delete from cumul_adresses where source='OD-NANTES';"
psql cadastre -c "insert into cumul_adresses (select wkb_geometry, numero, substr(adresse,length(numero)+2), null, concat(left(iris2008,5),rivoli), left(iris2008,5), null, '044', code_posta, 'OD-NANTES',null from import_nantes );"


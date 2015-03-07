cd /tmp
wget http://media.strasbourg.eu/alfresco/d/a/workspace/SpacesStore/455eab99-0974-4183-b2d8-6418f31e02f7/CUS_CUS_DUAH_ADR_20141501_1.zip
unzip /tmp/CUS_CUS_DUAH_ADR_20141501_1.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/RG_FIL_ADRESSE_POSTALE_line.shp -overwrite -nlt GEOMETRY -nln import_cus
psql cadastre -c "insert into cumul_adresses (select st_centroid(wkb_geometry) as geometrie, num as numero, nom_rue, null, null, concat(num_dept,num_comm), null,concat('0',num_dept), null, 'OD-CUS', null from import_cus);"


## http://opendata.grand-nancy.org/jeux-de-donnees/detail-dune-fiche-de-donnees/?tx_icsoddatastore_pi1%5Buid%5D=82&tx_icsoddatastore_pi1%5BreturnID%5D=447

cd /tmp
rm -rf ADRESSES*

wget http://opendata.grand-nancy.org/fileadmin/fichiers/opendata/Referentiel_adresse/ADRESSES_shp.zip
unzip ADRESSES_shp.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre ADRESSES.shp -overwrite -nlt GEOMETRY -nln import_nancy
psql cadastre -c "delete from cumul_adresses where source='OD-NANCY'; insert into cumul_adresses (select wkb_geometry, numvoie, nomvoie, null, concat('54',ccocom,rivoli), concat('54',ccocom),null,'054',null,'OD-NANCY',null from import_nancy);"


cd /tmp
rm -f adr_voie_lieu*

curl -o lyon.zip ' http://smartdata.grandlyon.com/smartdata/wp-content/plugins/wp-smartdata/proxy.php?format=Shape-zip&name=adr_voie_lieu.adrnumerovoie&commune=&href=https%$
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre /tmp/adr_voie_lieu.adrnumerovoie.shp -overwrite -nlt GEOMETRY -nln import_lyon
psql cadastre -c "delete from cumul_adresses where source='OD-LYON';"
psql cadastre -c "insert into cumul_adresses (select wkb_geometry, numero, voie, null, null, inseecommu, null, '069', null, 'OD-LYON',null from import_lyon);"
# mise à jour des codes FANTOIR
psql cadastre -c "with u as (select voie_cadastre as voie_m, insee_com as insee_m, fantoir_o from cumul_adresses m join (select insee_com as insee_o, fantoir as fantoir_o, voie_osm as voie_o from cumul_adresses where fantoir like '69%' and voie_osm is not null group by fantoir, voie_osm, insee_com) as o on (voie_o=voie_cadastre and insee_o=insee_com) where source='OD-LYON' and fantoir is null group by voie_cadastre, insee_com, fantoir_o) update cumul_adresses set fantoir=fantoir_o from u where insee_com=insee_m and voie_cadastre=voie_m and source='OD-LYON' and fantoir is null;"


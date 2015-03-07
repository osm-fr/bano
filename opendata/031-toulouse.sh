cd 031-toulouse
curl -o toulouse.zip 'https://data.toulouse-metropole.fr/les-donnees/-/opendata/card/12673-n-de-rue/resource/document?p_p_state=exclusive&_5_WAR_opendataportlet_jspPage=%2Fsearch%2Fview_card.jsp'
unzip -o toulouse.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre toulouse.vrt -overwrite -nlt GEOMETRY -nln import_toulouse
psql cadastre -c "begin; delete from cumul_adresses where source='OD-TOULOUSE'; insert into cumul_adresses (select wkb_geometry, regexp_replace(numero,'^0*',''), lib_off, null,concat(substr(sti,1,5),substr(rivoli,7,5)), substr(sti,1,5), null, '031', null, 'OD-TOULOUSE',null from import_toulouse);commit;"


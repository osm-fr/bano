cd 087_limoges
unzip -o export_bano_etalab_limoges.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre limoges_adresses.shp -overwrite -nlt GEOMETRY -nln import_limoges

# insertion données opendata dans cumul_adresse avec croisement fantoir_voie
psql cadastre -c " insert into cumul_adresses select wkb_geometry, numero, concat(i.type_voie, ' ', nom), concat(initcap(type_voie_),' ',nom_acc), concat(codcomm,rivoli_dgi,cle_rivoli), codcomm, null, '087', code_posta, 'OD-LIMOGES',null,null from import_limoges i join fantoir_voie f on (code_insee=codcomm and f.id_voie=rivoli_dgi);"



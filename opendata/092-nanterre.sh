cd 092_nanterre
rm -rf BDA_Adresse*

# récupération des shapefile contenant les points adresse
wget 'http://www.nanterre.fr/include/viewFile.php?idtf=11278&path=6a%2F11278_606_BDA_Adresse.zip' -O BDA_Adresse.zip
unzip -o BDA_Adresse.zip

# import dans postGIS
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre BDA_Adresse*.shp -overwrite -nlt GEOMETRY -nln import_nanterre

# création des adresses dans cumul_adresses avec données FANTOIR
psql cadastre -c "begin; delete from cumul_adresses where source='OD-NANTERRE'; insert into cumul_adresses (select wkb_geometry, trim( num_deb::text || ' ' || coalesce(suff_deb,'')), trim(type_voie || ' ' || nom_voie),voie_osm, '', code_insee, fantoir, '092', code_post, 'OD-NANTERRE', null, null from import_nanterre left join cumul_voies on (insee_com=code_insee::text and upper(voie_osm)=upper(type_voie || ' ' || nom_voie))); COMMIT;"


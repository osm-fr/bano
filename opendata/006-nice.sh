cd 006_nice
rm -rf ig*
wget 'http://opendata.nicecotedazur.org/data/storage/f/2014-12-08T15%3A52%3A26.440Z/ig-base-adresses-wgs84-shapefile.zip'
unzip -o ig-base-adresses-wgs84-shapefile.zip
ogr2ogr -t_srs EPSG:4326 -f PostgreSQL PG:dbname=cadastre ig_base_adresses_WGS84_shapefile.shp -overwrite -nlt GEOMETRY -nln import_nice

# insertion données opendata dans cumul_adresse, mais incomplètes (pas de code FANTOIR)
psql cadastre -c "delete from cumul_adresses where source='OD-NICE'; insert into cumul_adresses select wkb_geometry as geometrie, trim(concat(signca_i_4,' ',signca_i_5)) as numero, signca_i_6, '', '', signca_i_1, '','006',null,'OD-NICE',null,'' from import_nice where signca_i_4 != '0';"

# mise à jour code FANTOIR en se basant sur les données déjà présentes dans cumul_adresses
psql cadastre -c "with u as (select n.insee_com, n.voie_cadastre, b.fantoir from (select insee_com, voie_cadastre from cumul_adresses where source = 'OD-NICE' and fantoir='' group by 1,2) as n left join cumul_adresses b on (b.insee_com=n.insee_com and b.voie_osm=n.voie_cadastre and source not like 'OD%') where b.insee_com like '06%' group by 1,2,3) update cumul_adresses b set fantoir=u.fantoir from u where b.fantoir='' and b.source='OD-NICE' and b.insee_com=u.insee_com and b.voie_cadastre = u.voie_cadastre;"


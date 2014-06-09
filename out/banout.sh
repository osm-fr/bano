# ménage préparatoire...
rm -f bano-$1*

# export postgres > shapefile
export SHAPE_ENCODING='UTF-8'
ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 -s_srs "EPSG:4326" -t_srs "EPSG:4326" -overwrite bano-$1.shp PG:"dbname=cadastre" -sql "select * from (with u as (select fantoir,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir is not null and length(fantoir)=10 and fantoir like '$1%' group by fantoir,num) select concat(u.fantoir,'-',u.num) as id, upper(replace(case when u.num=o.num then o.numero when u.num=od.num then od.num else c.numero end,' ','')) as numero,coalesce(case when u.num=o.num then case when o.voie_osm != '' then replace(o.voie_osm,'’',chr(39)) else o.voie_cadastre end when u.num=od.num then replace(od.voie_osm,'’',chr(39)) else case when c.voie_osm!='' then replace(c.voie_osm,'’',chr(39)) else c.voie_cadastre end end, case when u.num=o.num then replace(o.voie_osm,'’',chr(39)) else (case when c.voie_osm !='' then replace(c.voie_osm,'’',chr(39)) else c.voie_cadastre end) end) as voie, ca.code_postal as code_post, coalesce(cn.nom,initcap(ca.nom_com)) as ville,case when u.num=o.num then 'OSM' when (u.num=od.num and od.voie_osm != od.voie_cadastre and od.voie_osm is not null) then 'O+O' when u.num=od.num then 'OD' when c.voie_osm != '' then 'C+O' else 'CAD' end as source, case when u.num=o.num then st_y(o.geometrie) when u.num=od.num then st_y(od.geometrie) else st_y(c.geometrie) end as lat,case when u.num=o.num then st_x(o.geometrie) when u.num=od.num then st_x(od.geometrie) else st_x(c.geometrie) end as lon,case when u.num=o.num then o.geometrie when u.num=od.num then od.geometrie else c.geometrie end as geom from u left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '$1%' and source='OSM') as o on (o.num=u.num and o.fantoir=u.fantoir) left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '$1%' and source='CADASTRE' and st_x(geometrie)!=0 and st_y(geometrie)!=0) as c on (c.num=u.num and c.fantoir=u.fantoir) left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '$1%' and source LIKE 'OD%' and voie_osm is not null and st_x(geometrie)!=0 and st_y(geometrie)!=0) as od on (od.num=u.num and od.fantoir=u.fantoir) left join code_cadastre ca on (ca.insee_com=left(u.fantoir,5)) left join communes cn on (cn.insee=left(u.fantoir,5) ) where u.num>'0') as data where lat is not null and lon is not null and numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' and numero !~'.[0-9 \\.\\-]{9,}' order by id"

# génération du .csv à partir du shapefile
ogr2ogr -f CSV bano-$1-tmp.csv -lco WRITE_BOM=YES bano-$1.shp
# suppression header + coupure à 6 décimale + tri
sed -e 1d bano-$1-tmp.csv | sed 's/\(\.[0-9]\{6\}\)[0-9]*/\1/g' | sort > bano-$1.csv

#exit

# copie dans le dossier web
mv bano-$1.csv /data/project/bano.openstreetmap.fr/web/data/

# préparation du shapefile zippé
cp -p -u /data/project/bano.openstreetmap.fr/web/data/*.txt ./
zip -q -9 bano-$1-shp.zip bano-$1.* .txt
chmod a+r *.zip
# copie dans le dossier web
mv bano-$1-shp.zip /data/project/bano.openstreetmap.fr/web/data/

# ménage
rm bano-$1*


exit

select * from (
with u as (select fantoir,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '69268%' and fantoir is not null group by fantoir,num)
select concat(u.fantoir,'-',u.num) as id, upper(replace(case when u.num=o.num then o.numero when u.num=od.num then od.num else c.numero end,' ','')) as numero,coalesce(case when u.num=o.num then case when o.voie_osm != '' then replace(o.voie_osm,'’',chr(39)) else o.voie_cadastre end when u.num=od.num then replace(od.voie_osm,'’',chr(39)) else case when c.voie_osm!='' then replace(c.voie_osm,'’',chr(39)) else c.voie_cadastre end end, case when u.num=o.num then replace(o.voie_osm,'’',chr(39)) else (case when c.voie_osm !='' then replace(c.voie_osm,'’',chr(39)) else c.voie_cadastre end) end) as voie, ca.code_postal as code_post, coalesce(cn.nom,initcap(ca.nom_com)) as ville,case when u.num=o.num then 'OSM' when (u.num=od.num and od.voie_osm != od.voie_cadastre and od.voie_osm is not null) then 'O+O' when u.num=od.num then 'OD' when c.voie_osm != '' then 'C+O' else 'CAD' end as source, case when u.num=o.num then st_y(o.geometrie) when u.num=od.num then st_y(od.geometrie) else st_y(c.geometrie) end as lat,case when u.num=o.num then st_x(o.geometrie) when u.num=od.num then st_x(od.geometrie) else st_x(c.geometrie) end as lon,case when u.num=o.num then o.geometrie when u.num=od.num then od.geometrie else c.geometrie end as geom
from u
left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '69%' and source='OSM') as o on (o.num=u.num and o.fantoir=u.fantoir)
left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '69%' and source='CADASTRE' and st_x(geometrie)!=0 and st_y(geometrie)!=0) as c on (c.num=u.num and c.fantoir=u.fantoir)
left join (select *,replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') as num from cumul_adresses where fantoir like '69%' and source LIKE 'OD%' and voie_osm is not null and st_x(geometrie)!=0 and st_y(geometrie)!=0) as od on (od.num=u.num and od.fantoir=u.fantoir)
left join code_cadastre ca on (ca.insee_com=left(u.fantoir,5))
left join communes cn on (cn.insee=left(u.fantoir,5) )
where u.num>'0'
) as data
where lat is not null and lon is not null and (upper(numero) !~ '^[0-9]{1,4}([A-Z]?.*)?' or numero ~'.[0-9 \.\-]{9,}') order by id;

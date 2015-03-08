# ménage préparatoire...
rm -f bano-$1*

# dédoublement des adresses multiple OSM (séparées par ';' '-' ',' ou 'à')
psql cadastre -q -c "insert into cumul_adresses select geometrie, trim( both from regexp_split_to_table(numero,';|-|à|,')), voie_cadastre, voie_osm, fantoir, insee_com, cadastre_com, dept, code_postal, source, batch_import_id, voie_fantoir from cumul_adresses where numero ~ ';|-|à|,' and insee_com like '$1%' and source='OSM';"
psql cadastre -q -c "delete from cumul_adresses where numero ~ ';|-|à|,' and insee_com like '$1%' and source='OSM';"

# export postgres > shapefile
export SHAPE_ENCODING='UTF-8'
ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 -s_srs "EPSG:4326" -t_srs "EPSG:4326" -overwrite bano-$1.shp PG:"dbname=cadastre" -sql " \
SELECT * \
FROM (WITH u AS \
        (SELECT fantoir, \
                replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num \
         FROM cumul_adresses \
         WHERE fantoir IS NOT NULL \
           AND length(fantoir)=10 \
           AND fantoir LIKE '$1%' \
         GROUP BY fantoir, \
                  num), lp as (select insee, min(cp) as cp from laposte_cp where insee like '$1%' group by 1) \
      SELECT concat(u.fantoir,'-',u.num) AS id, \
             upper(replace(CASE WHEN u.num=o.num THEN o.numero WHEN u.num=od.num THEN od.num ELSE c.numero END,' ','')) AS numero, \
             replace(replace(regexp_replace(regexp_replace(coalesce(CASE \
             	WHEN u.num=o.num THEN \
             	CASE \
             		WHEN o.voie_osm != '' THEN replace(o.voie_osm,'’',chr(39)) \
             		ELSE o.voie_cadastre \
             	END \
             	WHEN u.num=od.num THEN \
		CASE \
			WHEN od.voie_osm is not null THEN replace(od.voie_osm,'’',chr(39)) \
			ELSE od.voie_cadastre \
		END \
             	ELSE \
             	CASE \
             		WHEN c.voie_osm!='' THEN replace(c.voie_osm,'’',chr(39)) \
             		ELSE c.voie_cadastre \
             	END \
             END, \
             CASE \
             	WHEN u.num=o.num THEN replace(o.voie_osm,'’',chr(39)) \
             	ELSE \
             	CASE \
             		WHEN c.voie_osm !='' THEN replace(c.voie_osm,'’',chr(39)) \
             		ELSE c.voie_cadastre \
             	END \
             END),'([dD][eé]partementale?|Rue|[rR]urale?|[vV]icinale?|[cC]ommunale?|Cr) ([0-9]+ )?[dD]ite? ',''),'(Draille|Chemin|Sentier) [dD]ite? ','\1 '),'Voie Che ','Chemin '),'Cours Dit Che ','Chemin ') AS voie, \
             coalesce(cp.postal_cod, lp.cp, ca.code_postal) AS code_post, \
             coalesce(cn.nom,initcap(ca.nom_com)) AS ville, \
             CASE \
                 WHEN u.num=o.num THEN 'OSM' \
                 WHEN (u.num=od.num \
                       AND od.voie_osm != od.voie_cadastre \
                       AND od.voie_osm IS NOT NULL) THEN 'O+O' \
                 WHEN u.num=od.num THEN 'OD' \
                 WHEN c.voie_osm != '' THEN 'C+O' \
                 ELSE 'CAD' \
             END AS SOURCE, \
             CASE \
                 WHEN u.num=o.num THEN st_y(o.geometrie) \
                 WHEN u.num=od.num THEN st_y(od.geometrie) \
                 ELSE st_y(c.geometrie) \
             END AS lat, \
             CASE \
                 WHEN u.num=o.num THEN st_x(o.geometrie) \
                 WHEN u.num=od.num THEN st_x(od.geometrie) \
                 ELSE st_x(c.geometrie) \
             END AS lon, \
             CASE \
                 WHEN u.num=o.num THEN o.geometrie \
                 WHEN u.num=od.num THEN od.geometrie \
                 ELSE c.geometrie \
             END AS geom \
      FROM u \
      LEFT JOIN lp ON (lp.insee=left(u.fantoir,5)) \
      LEFT JOIN \
        (SELECT *, \
                replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num \
         FROM cumul_adresses \
         WHERE fantoir LIKE '$1%' \
           AND SOURCE='OSM') AS o \
        ON (o.num=u.num AND o.fantoir=u.fantoir) \
      LEFT JOIN \
        (SELECT *, \
                replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num \
         FROM cumul_adresses \
         WHERE fantoir LIKE '$1%' \
           AND SOURCE='CADASTRE' \
           AND st_x(geometrie)!=0 \
           AND st_y(geometrie)!=0) AS c \
        ON (c.num=u.num AND c.fantoir=u.fantoir) \
      LEFT JOIN \
        (SELECT *, \
                replace(replace(replace(replace(replace(replace(replace(regexp_replace(upper(numero),'^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',',') AS num \
         FROM cumul_adresses \
         WHERE fantoir LIKE '$1%' \
           AND SOURCE LIKE 'OD%' \
           AND st_x(geometrie)!=0 \
           AND st_y(geometrie)!=0) AS od \
        ON (od.num=u.num AND od.fantoir=u.fantoir) \
      LEFT JOIN code_cadastre ca \
      	ON (ca.insee_com=left(u.fantoir,5)) \
      LEFT JOIN communes cn \
      	ON (cn.insee=left(u.fantoir,5)) \
      LEFT JOIN postal_code cp \
      	ON (cp.insee = left(u.fantoir,5) and st_contains(cp.wkb_geometry, coalesce(o.geometrie, od.geometrie, c.geometrie))) \
      WHERE u.num>'0') AS DATA \
WHERE lat IS NOT NULL \
  AND lon IS NOT NULL \
  AND numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?' \
  AND numero !~'.[0-9 \\.\\-]{9,}' \
ORDER BY id \
"

# génération du .csv à partir du shapefile
ogr2ogr -f CSV bano-$1-tmp.csv -lco WRITE_BOM=YES bano-$1.shp
# suppression header + coupure à 6 décimale + tri
sed -e 1d bano-$1-tmp.csv | sed 's/\(\.[0-9]\{6\}\)[0-9]*/\1/g' | sort > bano-$1.csv

#exit

# sortie RDF "turtle" à partir du csv
python csv2ttl.py bano-$1.csv $1 > bano-$1.ttl
gzip -9 bano-$1.ttl
mv bano-$1.ttl.gz /data/project/bano.openstreetmap.fr/web/data/

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

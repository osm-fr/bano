#!/bin/bash

set -e

# script écrit et maintenu par cquest@openstreetmap.fr

OUTPUT=bano-$1.json
# dédoublement des adresses multiple OSM (séparées par ';' '-' ',' ou 'à')
psql cadastre -q -c "insert into cumul_adresses select geometrie, trim( both from regexp_split_to_table(numero,';|-|à|,')), voie_cadastre, voie_osm, fantoir, insee_com, cadastre_com, dept, code_postal, source, batch_import_id, voie_fantoir from cumul_adresses where numero ~ ';|-|à|,' and insee_com like '$1%' and source='OSM';"
psql cadastre -q -c "delete from cumul_adresses where numero ~ ';|-|à|,' and insee_com like '$1%' and source='OSM';"

rm -f $OUTPUT


echo "`date +%H:%M:%S` Communes $1"
# export des communes
psql cadastre -t -A -c " \
SELECT '{\"id\": \"' || insee || '\",\"type\": \"' || CASE WHEN population<1 THEN 'village' WHEN population<'10' THEN 'town' ELSE 'city' END  || '\",\"name\": \"' || g.nom || '\",\"postcode\": \"' || ca.code_postal || '\",\"lat\": \"' || round(lat_chf,6) || '\",\"lon\": \"' || round(lon_chf,6) || '\",\"city\": \"' || g.nom|| '\",\"departement\": \"' || cog.nom_dep || '\", \"region\": \"' || cog.nom_reg || '\", \"population\": ' || population || ', \"adm_weight\": ' || CASE WHEN statut LIKE 'Capital%' THEN 6 WHEN statut = 'Préfecture de régi' THEN 5 WHEN statut='Préfecture' THEN 4 WHEN statut LIKE 'Sous-pr%' THEN 3 WHEN statut='Chef-lieu canton' THEN 2 ELSE 1 END || ', \"importance\": ' || greatest(0.075,round(log((CASE WHEN statut LIKE 'Capital%' THEN 6 WHEN statut = 'Préfecture de régi' THEN 5 WHEN statut='Préfecture' THEN 4 WHEN statut LIKE 'Sous-pr%' THEN 3 WHEN statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(population+1)/3),4)) || '}' \
FROM geofla_plus g join code_cadastre ca on (ca.insee_com=insee) join (select dep, nom_dep, nom_reg from cog group by dep,nom_dep, nom_reg) as cog on (cog.dep=left(insee,2) or cog.dep=left(insee,3)) WHERE insee like '$1%' order by insee; \
" | grep id >> $OUTPUT


echo "`date +%H:%M:%S` Voie non rapprochées $1";
# export fantoir_voie (pour les voies non rapprochées) + cumul_adresse (ponctuel adresse) > json
for com in `psql cadastre -c "SELECT insee FROM communes where insee like '$1%';" -A -t`; do psql cadastre -t -A -c " \
SET client_min_messages TO WARNING; WITH v as (select code_insee as insee_com, code_insee || id_voie || cle_rivoli as fantoir from fantoir_voie f left join cumul_voies v on (v.insee_com = '$com' AND f.code_insee=v.insee_com and v.fantoir = code_insee || id_voie || cle_rivoli) where v.fantoir is null and code_insee = '$com')
SELECT '{\"id\": \"' || osm.fantoir || CASE WHEN coalesce(cp.postal_cod, cad.code_postal)!=cad.code_postal THEN ('_' || cp.postal_cod) ELSE '' END || '\",\"citycode\":\"' || left(osm.fantoir,5) || '\",\"type\": \"street\",\"name\": \"' || replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(regexp_replace(max(case when osm.voie_osm !='' then osm.voie_osm else osm.voie_cadastre end),'^IMP ','Impasse '),'^RTE ','Route '),'^ALL ','Allée '),'^PL ','Place '),'^PLA ','Place '),'^AV ','Avenue '),'^LOT ','Lotissement '),'^RES ','Résidence '),'^CHEM ','Chemin '),'^RLE ','Ruelle '),'^BD ','Boulevard '),'^SQ ','Square '),'^PAS ','Passage '),'^SEN ','Sentier '),'^CRS ','Cours '),'^TRA ','Traverse '),'^MTE ','Montée '),'^RPT ','Rond-point '),'^HAM ','Hameau '),'^VLA ','Villa '),'^PROM ','Promenade '),'^ESP ','Esplanade '),'^FG ','Faubourg '),'^TSSE ','Terrasse '),'^CTRE ','Centre '),'^PASS ','Passerelle '),'^FRM ','Ferme '),' GAL ',' Général '),' MAL ',' Maréchal '),' ST ',' Saint '),' STE ',' Sainte '),' PDT ',' Président '),' HT ',' Haut '),' HTE ',' Haute '),' VX ',' Vieux '),' PTE ',' Petite '),'\"',''),'’',chr(39)) || '\",\"postcode\": \"' || coalesce(cp.postal_cod, min(lp.cp), cad.code_postal) || CASE WHEN replace(lower(cp.nom),'-',' ') != replace(lower(c.nom),'-',' ') THEN '\",\"post_office\": \"' || cp.nom ELSE '' END || '\",\"lat\": \"' || round(st_y(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6) || '\",\"lon\": \"' || round(st_x(st_centroid(st_convexhull(ST_Collect(osm.geometrie))))::numeric,6) || '\",\"city\": \"' || c.nom || '\",\"departement\": \"' || cog.nom_dep || '\", \"region\": \"' || cog.nom_reg || '\",\"importance\": '|| round(log((CASE WHEN (cad.code_postal LIKE '75%' OR g.statut LIKE 'Capital%') THEN 6 WHEN (cad.code_postal LIKE '690%' OR cad.code_postal LIKE '130%' OR g.statut = 'Préfecture de régi') THEN 5 WHEN g.statut='Préfecture' THEN 4 WHEN g.statut LIKE 'Sous-pr%' THEN 3 WHEN g.statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(g.population+1)/3)::numeric*log(1+log(count(osm.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(osm.geometrie)),st_convexhull(ST_Collect(osm.geometrie)))::geography)+1)+log(CASE WHEN max(osm.voie_cadastre) like 'Boulevard%' THEN 4 WHEN max(osm.voie_cadastre) LIKE 'Place%' THEN 4 WHEN max(osm.voie_cadastre) LIKE 'Espl%' THEN 4 WHEN max(osm.voie_cadastre) LIKE 'Av%' THEN 3 WHEN max(osm.voie_cadastre) LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) ||' ,\"housenumbers\":' || concat('{',string_agg(DISTINCT concat('\"',replace(replace(replace(osm.numero,' ',''),'\"',''),'\\',''),'\": {\"lat\": ',round(st_y(osm.geometrie)::numeric,6),',\"lon\": ',round(st_x(osm.geometrie)::numeric,6),'}'), ','),'}}') AS sjson
FROM v
LEFT JOIN cumul_adresses osm ON (osm.fantoir=v.fantoir)
JOIN communes c ON (c.insee=v.insee_com)
JOIN code_cadastre cad ON (cad.insee_com=v.insee_com)
JOIN
  (SELECT fantoir,
          replace(numero,' ','') AS num,
          max(SOURCE) AS src
   FROM cumul_adresses
   WHERE fantoir like '$com%'
   GROUP BY 1,
            2) AS b ON (b.fantoir=osm.fantoir
                        AND osm.SOURCE=b.src
                        AND b.num=replace(osm.numero,' ',''))
LEFT JOIN (select dep, nom_dep, nom_reg from cog group by dep, nom_dep, nom_reg) as cog ON (cog.dep=left(v.insee_com,2) or cog.dep=left(v.insee_com,3))
LEFT JOIN geofla_plus g ON (g.insee=v.insee_com)
LEFT JOIN laposte_cp lp ON (lp.insee=v.insee_com)
LEFT JOIN postal_code cp ON (cp.insee=v.insee_com AND ST_Contains(cp.wkb_geometry, osm.geometrie))
WHERE osm.fantoir IS NOT NULL
  AND osm.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?'
  AND osm.numero !~'.[0-9 \\.\\-]{9,}'
  AND cad.insee_com = '$com'
  AND c.insee = '$com'
  AND g.insee = '$com'
GROUP BY osm.fantoir,
         cad.code_postal, cp.postal_cod,
         c.nom, cp.nom,
         cog.nom_dep,
         cog.nom_reg,
         g.statut,
         g.population
ORDER BY osm.fantoir;
" >> $OUTPUT; done

echo "`date +%H:%M:%S` Voie rapprochées $1"
# export cumul_voie (position centre de voirie) + cumul_adresse (ponctuel adresse) > json
for com in `psql cadastre -c "SELECT insee FROM communes where insee like '$1%';" -A -t`; do psql cadastre -t -A -c " \
SET client_min_messages TO WARNING; SELECT '{\"id\": \"' || v.fantoir || CASE WHEN coalesce(cp.postal_cod, cad.code_postal)!=cad.code_postal THEN ('_' || cp.postal_cod) ELSE '' END || '\",\"citycode\": \"' || left(v.fantoir,5) || '\",\"type\": \"street\",\"name\": \"' || replace(replace(v.voie_osm,'\"',''),'’',chr(39)) || '\",\"postcode\": \"' || coalesce(cp.postal_cod, min(lp.cp), cad.code_postal) || CASE WHEN replace(lower(cp.nom),'-',' ') != replace(lower(c.nom),'-',' ') THEN '\",\"post_office\": \"' || cp.nom ELSE '' END || '\",\"lat\": \"' || round(st_y(v.geometrie)::numeric,6) || '\",\"lon\": \"' || round(st_x(v.geometrie)::numeric,6) || '\",\"city\": \"' || c.nom || '\",\"departement\": \"' || cog.nom_dep || '\", \"region\": \"' || cog.nom_reg || '\",\"importance\": '|| round(log((CASE WHEN (cad.code_postal LIKE '75%' OR g.statut LIKE 'Capital%') THEN 6 WHEN (cad.code_postal LIKE '690%' OR cad.code_postal LIKE '130%' OR g.statut = 'Préfecture de régi') THEN 5 WHEN g.statut='Préfecture' THEN 4 WHEN g.statut LIKE 'Sous-pr%' THEN 3 WHEN g.statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(g.population+1)/3)::numeric*log(1+log(count(a.*)+1)+log(st_length(st_longestline(st_convexhull(ST_Collect(a.geometrie)),st_convexhull(ST_Collect(a.geometrie)))::geography)+1)+log(CASE WHEN v.voie_osm like 'Boulevard%' THEN 4 WHEN v.voie_osm LIKE 'Place%' THEN 4 WHEN v.voie_osm LIKE 'Espl%' THEN 4 WHEN v.voie_osm LIKE 'Av%' THEN 3 WHEN v.voie_osm LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) ||' ,\"housenumbers\":' || concat('{',string_agg(DISTINCT concat('\"',replace(replace(replace(a.numero,' ',''),'\"',''),'\\',''),'\": {\"lat\": ',round(st_y(a.geometrie)::numeric,6),',\"lon\": ',round(st_x(a.geometrie)::numeric,6),'}'), ','),'}}') AS sjson
FROM cumul_voies v
JOIN communes c ON (insee=insee_com)
JOIN code_cadastre cad ON (cad.insee_com=v.insee_com)
LEFT JOIN cumul_adresses a ON (a.fantoir=v.fantoir)
JOIN
  (SELECT fantoir,
          replace(numero,' ','') AS num,
          max(SOURCE) AS src
   FROM cumul_adresses
   WHERE fantoir LIKE '$com%'
   GROUP BY 1,
            2) AS b ON (b.fantoir=a.fantoir
                        AND a.SOURCE=b.src
                        AND b.num=replace(a.numero,' ',''))
LEFT JOIN (select dep, nom_dep, nom_reg from cog group by dep, nom_dep, nom_reg) as cog ON (cog.dep=left(v.insee_com,2) or cog.dep=left(v.insee_com,3))
LEFT JOIN geofla_plus g ON (g.insee=v.insee_com)
LEFT JOIN laposte_cp lp ON (lp.insee=v.insee_com)
LEFT JOIN postal_code cp ON (cp.insee=v.insee_com AND ST_Contains(cp.wkb_geometry, a.geometrie))
WHERE v.fantoir LIKE '$com%'
  AND a.numero ~ '^[0-9]{1,4}( ?[A-Z]?.*)?'
  AND a.numero !~'.[0-9 \\.\\-]{9,}'
  AND cad.insee_com = '$com'
  AND c.insee = '$com'
  AND g.insee = '$com'
GROUP BY v.fantoir,
         v.voie_osm,
         cad.code_postal, cp.postal_cod,
         v.geometrie,
         c.nom, cp.nom,
         cog.nom_dep,
         cog.nom_reg,
         g.statut,
         g.population
ORDER BY v.fantoir;
" >> $OUTPUT; done


echo "`date +%H:%M:%S` Voie rapprochées sans adresses $1"
# export cumul_voie (position centre de voirie) > json
psql cadastre -t -A -c " \
SET client_min_messages TO WARNING; SELECT '{\"id\": \"' || v.fantoir || CASE WHEN coalesce(cp.postal_cod, cad.code_postal)!=cad.code_postal THEN ('_' || cp.postal_cod) ELSE '' END || '\",\"citycode\": \"' || left(v.fantoir,5) || '\",\"type\": \"street\",\"name\": \"' || replace(replace(v.voie_osm,'\"',''),'’',chr(39)) || '\",\"postcode\": \"' || coalesce(cp.postal_cod, min(lp.cp), cad.code_postal) || CASE WHEN replace(lower(cp.nom),'-',' ') != replace(lower(c.nom),'-',' ') THEN '\",\"post_office\": \"' || cp.nom ELSE '' END || '\",\"lat\": \"' || round(st_y(v.geometrie)::numeric,6) || '\",\"lon\": \"' || round(st_x(v.geometrie)::numeric,6) || '\",\"city\": \"' || c.nom || '\",\"departement\": \"' || cog.nom_dep || '\", \"region\": \"' || cog.nom_reg || '\",\"importance\": '|| round(log((CASE WHEN (cad.code_postal LIKE '75%' OR g.statut LIKE 'Capital%') THEN 6 WHEN (cad.code_postal LIKE '690%' OR cad.code_postal LIKE '130%' OR g.statut = 'Préfecture de régi') THEN 5 WHEN g.statut='Préfecture' THEN 4 WHEN g.statut LIKE 'Sous-pr%' THEN 3 WHEN g.statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(g.population+1)/3)::numeric*log(1+log(count(a.*)+1)+log(CASE WHEN v.voie_osm like 'Boulevard%' THEN 4 WHEN v.voie_osm LIKE 'Place%' THEN 4 WHEN v.voie_osm LIKE 'Espl%' THEN 4 WHEN v.voie_osm LIKE 'Av%' THEN 3 WHEN v.voie_osm LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4) ||' }' AS sjson
FROM cumul_voies v
JOIN communes c ON (insee=insee_com)
JOIN code_cadastre cad ON (cad.insee_com=v.insee_com)
LEFT JOIN cumul_adresses a ON (a.fantoir=v.fantoir)
LEFT JOIN (select dep, nom_dep, nom_reg from cog group by dep, nom_dep, nom_reg) as cog ON (cog.dep=left(v.insee_com,2) or cog.dep=left(v.insee_com,3))
LEFT JOIN geofla_plus g ON (g.insee=v.insee_com)
LEFT JOIN laposte_cp lp ON (lp.insee=v.insee_com)
LEFT JOIN postal_code cp ON (cp.insee=v.insee_com AND ST_Contains(cp.wkb_geometry, v.geometrie))
WHERE v.fantoir LIKE '$1%'
  AND a.numero IS NULL
  AND cad.insee_com like '$1%'
  AND c.insee like '$1%'
  AND g.insee like '$1%'
GROUP BY v.fantoir,
         v.voie_osm,
         cad.code_postal, cp.postal_cod,
         v.geometrie,
         c.nom, cp.nom,
         cog.nom_dep,
         cog.nom_reg,
         g.statut,
         g.population
ORDER BY v.fantoir;
" >> $OUTPUT


echo "`date +%H:%M:%S` LD $1"
# export cumul_place (lieux-dits) > json
psql cadastre -t -A -c "
SET client_min_messages TO WARNING;
WITH u AS (select fantoir as f, insee_com as insee from cumul_places where fantoir like '$1%' GROUP BY 1,2), lp as (select insee, min(cp) as cp from laposte_cp where insee like '$1%' group by 1)
select DISTINCT '{\"id\": \"' || u.f
        || '\",\"citycode\": \"' || left(u.f,5)
	|| '\",\"type\": \"' || 'place'
	|| '\",\"name\": \"' || replace(replace(coalesce(o.libelle_osm, c.libelle_cadastre),'\"',''),'’',chr(39))
	|| '\",\"postcode\": \"' || coalesce(cp.postal_cod, lp.cp, ca.code_postal) || CASE WHEN replace(lower(cp.nom),'-',' ') != replace(lower(coalesce(cn.nom,initcap(ca.nom_com))),'-',' ') THEN '\",\"post_office\": \"' || cp.nom ELSE '' END
	|| '\",\"lat\": \"' || case when o.geometrie is not null then round(st_y(o.geometrie)::numeric,6) else st_y(c.geometrie) end
	|| '\",\"lon\": \"' || case when o.geometrie is not null then round(st_x(o.geometrie)::numeric,6) else st_x(c.geometrie) end
	|| '\",\"city\": \"' || coalesce(cn.nom,initcap(ca.nom_com))
	|| '\",\"departement\": \"' || cog.nom_dep
	|| '\", \"region\": \"' || cog.nom_reg
	|| '\", \"importance\": '|| least(0.05,round(log((CASE WHEN g.statut LIKE 'Capital%' THEN 6 WHEN g.statut = 'Préfecture de régi' THEN 5 WHEN g.statut='Préfecture' THEN 4 WHEN g.statut LIKE 'Sous-pr%' THEN 3 WHEN g.statut='Chef-lieu canton' THEN 2 ELSE 1 END)+log(g.population+1)/3)*(0.25+0.5*(1-('0' || coalesce(f.ld_bati,'1'))::numeric)),4))
	||'}'
from u
	LEFT JOIN fantoir_voie f on (f.code_insee=u.insee AND u.f = concat(f.code_insee,f.id_voie,f.cle_rivoli))
	LEFT JOIN cumul_places c on (c.fantoir=u.f and c.source='CADASTRE')
	LEFT JOIN cumul_places o on (o.fantoir=u.f and o.source='OSM')
	LEFT JOIN code_cadastre ca ON (ca.insee_com=u.insee)
	LEFT JOIN communes cn ON (cn.insee=u.insee)
	LEFT JOIN geofla_plus g ON (g.insee=u.insee)
	LEFT JOIN lp ON (lp.insee=u.insee)
    LEFT JOIN postal_code cp ON (cp.insee=u.insee AND ST_Contains(cp.wkb_geometry, o.geometrie))
	JOIN (select dep, nom_dep, nom_reg from cog group by dep, nom_dep, nom_reg) as cog ON (cog.dep=left(u.insee,2) or cog.dep=left(u.insee,3))
where coalesce(o.libelle_osm, c.libelle_cadastre) != cn.nom ORDER BY 1;
" >> $OUTPUT


echo "`date +%H:%M:%S` FIN $1"


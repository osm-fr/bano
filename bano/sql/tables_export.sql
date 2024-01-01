-- codes postaux
-- ne prendre dans planet_osm_postal_code que les CPs avec un boundary != '' et un ref:insee != ''
--
-- construire la table des insee | [CPs] à partir de la table codes_postaux de La Poste
-- utiliser cette table pour l'export des communes
--
-- s'appuyer sur cette table pour déterminer la géometrie infra communale des CPs des communes pluri-distribuées
-- utiliser les polygones issus de ce croisement en jointure ouverte pour les points nommes et les adresses, avec comme fallback la table des codes_postaux par commune si jointure nulle
-- possibilité : faire un cross join par commune pluri-distribuée et en sortir un distinct (geometrie,cp)

CREATE TEMP TABLE sub_cp
AS
SELECT  ST_Subdivide(way) AS way,
        "ref:INSEE",
        postal_code
FROM    planet_osm_postal_code
WHERE   COALESCE(postal_code,'') != '';

DROP TABLE IF EXISTS numeros_export CASCADE;
CREATE UNLOGGED TABLE numeros_export
AS
WITH
cp_fantoir
AS
(SELECT fantoir,
        MIN(code_postal) AS min_cp
FROM    bano_adresses
GROUP BY 1),
num_norm
AS
(SELECT REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REGEXP_REPLACE(UPPER(numero),
                        '^0*',''),'BIS','B'),'TER','T'),'QUATER','Q'),'QUAT','Q'),' ',''),'à','-'),';',','),'"','') AS num,
        *
FROM    bano_adresses),
num_norm_id
AS
(SELECT fantoir||'-'||num AS id_add,
        row_number() OVER (PARTITION BY fantoir||num ORDER BY CASE WHEN source = 'OSM' THEN 1 ELSE 2 END) AS rang,
        *
FROM    num_norm)
SELECT  dep,
        n.code_insee,
        n.fantoir,
        id_add,
        numero,
        nom_voie,
        COALESCE(code_postal,cp.postal_code,min_cp) code_postal,
        cn.libelle,
        source,
        lat,
        lon,
        geometrie
FROM    num_norm_id n
JOIN    cog_commune cn 
ON      (cn.com = code_insee) 
LEFT OUTER JOIN sub_cp cp 
ON      (cp."ref:INSEE" = code_insee AND
        ST_Contains(cp.way, geometrie)) 
LEFT OUTER JOIN cp_fantoir
USING   (fantoir)
WHERE   rang = 1;

-- CREATE INDEX idx_numeros_export_code_insee ON numeros_export(code_insee);
CREATE INDEX idx_numeros_export_dep ON numeros_export(dep);

DROP TABLE IF EXISTS numeros_export_importance CASCADE;
CREATE UNLOGGED TABLE numeros_export_importance
AS
SELECT dep,
       fantoir,
       ST_Length(ST_Transform(ST_Longestline(ST_Convexhull(ST_Collect(geometrie)),ST_Convexhull(ST_Collect(geometrie))),3857)) AS longueur_max,
       count(*) AS nombre_adresses
FROM   numeros_export
GROUP BY dep,
         fantoir;
         
CREATE INDEX idx_numeros_export_importance_dep ON numeros_export_importance(dep);

DROP TABLE IF EXISTS export_voies_adresses_json CASCADE;
CREATE UNLOGGED TABLE export_voies_adresses_json
AS
SELECT fantoir AS id,
       ne.code_insee AS citycode,
       'street' AS type,
       REPLACE(REPLACE(REGEXP_REPLACE(nom_voie,'\t',' '),'"',chr(39)),'’',chr(39)) AS name,
       code_postal AS postcode,
       ROUND(pn.lat::numeric,6)::float AS lat,
       ROUND(pn.lon::numeric,6)::float AS lon,
       nom_com AS city,
       nom_dep AS departement,
       nom_reg AS region,
       ROUND(LOG(c.adm_weight+LOG(c.population+1)/3)::numeric*LOG(1+LOG(nombre_adresses+1)+LOG(longueur_max+1)+LOG(CASE WHEN nom_voie like 'Boulevard%' THEN 4 WHEN nom_voie LIKE 'Place%' THEN 4 WHEN nom_voie LIKE 'Espl%' THEN 4 WHEN nom_voie LIKE 'Av%' THEN 3 WHEN nom_voie LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4)::float AS importance,
       string_agg(numero||'$'||ROUND(ne.lat::numeric,6)::text||'$'||ROUND(ne.lon::numeric,6)::text,'@' ORDER BY numero) AS housenumbers
FROM   numeros_export ne
JOIN   cog_pyramide_admin AS cog
USING  (code_insee)
JOIN   (SELECT fantoir,
               lon,
               lat
       FROM    bano_points_nommes) AS pn
USING  (fantoir)
JOIN   infos_communes c
USING  (code_insee)
JOIN   numeros_export_importance
USING  (fantoir)
GROUP BY 1,2,3,4,5,6,7,8,9,10,11
ORDER BY 1;

CREATE INDEX idx_export_voies_adresses_json_dep ON export_voies_adresses_json(dep);

DROP TABLE IF EXISTS export_voies_sans_adresses_json CASCADE;
CREATE UNLOGGED TABLE export_voies_sans_adresses_json
AS
WITH
set_fantoir
AS
(SELECT fantoir FROM bano_points_nommes
EXCEPT
SELECT fantoir FROM numeros_export)
SELECT pn.fantoir AS id,
       pn.code_insee AS citycode,
           nature,
           CASE
               WHEN nature = 'place' THEN 'place'
                   WHEN nature = 'lieu-dit' THEN 'place'
                   ELSE 'street'
           END AS type,
       REPLACE(REPLACE(REGEXP_REPLACE(nom,'\t',' '),'"',chr(39)),'’',chr(39)) AS name,
--       code_postal AS postcode,
       ROUND(pn.lat::numeric,6)::float AS lat,
       ROUND(pn.lon::numeric,6)::float AS lon,
       nom_com AS city,
       nom_dep AS departement,
       nom_reg AS region,
           CASE
               WHEN nature IN ('place','lieu-dit') THEN 0.05
                   ELSE ROUND(LOG(c.adm_weight+LOG(c.population+1)/3)::numeric*LOG(1+LOG(CASE WHEN nom like 'Boulevard%' THEN 4 WHEN nom LIKE 'Place%' THEN 4 WHEN nom LIKE 'Espl%' THEN 4 WHEN nom LIKE 'Av%' THEN 3 WHEN nom LIKE 'Rue %' THEN 2 ELSE 1 END))::numeric,4)::float
           END AS importance,
           source,
           RANK() OVER (PARTITION BY fantoir ORDER BY CASE source WHEN 'OSM' THEN 1 ELSE 2 END, CASE nature WHEN 'centroide' THEN 2 ELSE 1 END)
FROM   set_fantoir
--JOIN   (select * from bano_points_nommes where code_insee = '85172') pn
JOIN   bano_points_nommes AS pn
USING  (fantoir)
JOIN   cog_pyramide_admin AS cog
USING  (code_insee)
JOIN   infos_communes c
USING  (code_insee)
ORDER BY 1
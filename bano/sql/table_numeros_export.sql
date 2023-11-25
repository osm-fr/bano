CREATE TEMP TABLE sub_cp
AS
SELECT  ST_Subdivide(way) AS way,
        "ref:INSEE",
        postal_code
FROM    planet_osm_postal_code
WHERE   COALESCE(postal_code,'') != '';

DROP TABLE IF EXISTS numeros_export CASCADE;
CREATE TABLE numeros_export
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

CREATE INDEX idx_numeros_export_code_insee ON numeros_export(code_insee);
CREATE INDEX idx_numeros_export_dep ON numeros_export(dep);
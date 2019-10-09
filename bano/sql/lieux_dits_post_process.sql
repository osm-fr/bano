DELETE FROM cadastre_2_place WHERE insee_com like '__dept__%';
WITH
fantoir 
AS
(SELECT DISTINCT code_insee||id_voie||cle_rivoli AS fantoir,
                 TRIM(BOTH FROM nature_voie||' '||libelle_voie)   AS nom,
                 code_insee AS insee_com
FROM fantoir_voie
WHERE code_insee LIKE '__dept__%' AND
      type_voie = '3'),
lieux_dits
AS
(SELECT ST_Centroid(geometrie) AS geometrie,
        regexp_replace(regexp_replace(nom,'   ',' ','g'),'  ',' ','g') AS nom,
        insee_com
FROM lieux_dits
WHERE insee_com LIKE '__dept__%' AND
      nom IS NOT NULL ),
mix
AS
(SELECT l.*,
        f.fantoir
FROM lieux_dits l
LEFT OUTER JOIN fantoir f
USING (nom,insee_com))
INSERT INTO cadastre_2_place
SELECT geometrie,
       nom,
       fantoir,
       insee_com
FROM	 mix;
COMMIT;
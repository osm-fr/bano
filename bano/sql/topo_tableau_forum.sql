WITH
t
AS
(SELECT SUBSTR(code,1,5) AS com,COUNT(*)
FROM    topo_comparaison
WHERE   a_ajouter OR a_maj
GROUP BY 1),
f
AS
(SELECT dep,libelle,count,com
FROM    cog_commune JOIN t
USING   (com)
WHERE   typecom = 'COM'
ORDER BY 3 DESC)
SELECT  dep,
        com,
        libelle,
        count
FROM f
UNION ALL
SELECT 'stats topo stage','date',max(date_creation)::text,COUNT(*)
FROM topo_stage


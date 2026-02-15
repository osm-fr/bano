WITH
cnt
AS
(SELECT SUBSTR(code,1,5) AS code_insee,COUNT(*)
FROM topo_comparaison
WHERE a_ajouter OR a_maj
GROUP BY 1)
SELECT code_insee
FROM cnt
ORDER BY count DESC;
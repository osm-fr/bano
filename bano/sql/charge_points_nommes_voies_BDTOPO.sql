WITH
fantoir
AS
(SELECT fantoir,
        TRIM (BOTH FROM (COALESCE(nature_voie,'')||' '||libelle_voie)) AS nom
FROM    topo
WHERE   code_insee = '__code_insee__' AND
        COALESCE(caractere_annul,'x') NOT IN ('O','Q')),
lignes_subdiv
AS
(SELECT  nom_collaboratif AS nom,
        COALESCE(a9.code_insee,'xxxxx') as insee_jointure,
        a9.code_insee insee_ac,
        a9.nom nom_ac,
        b.geometrie
FROM    (SELECT * FROM bdtopo_voie_nommee WHERE code_insee = '__code_insee__' AND COALESCE(identifiant_voie_ban,'') = '' )b
LEFT OUTER JOIN (SELECT * FROM polygones_insee_a9 WHERE insee_a8 = '__code_insee__') a9
ON      ST_Intersects(b.geometrie, a9.geometrie)),
lignes_agregees
AS
(SELECT ST_Collect(geometrie) geometrie,
        nom,
        insee_ac,
        nom_ac,
        insee_jointure
FROM    lignes_subdiv
GROUP BY 2,3,4,5),
resultat
AS
(SELECT ST_ClosestPoint(geometrie,ST_Centroid(geometrie)) AS geometrie,
       nom,
       fantoir,
       insee_ac,
       nom_ac
FROM   lignes_agregees
LEFT OUTER JOIN fantoir
USING (nom))
SELECT ST_X(geometrie),
       ST_Y(geometrie),
       nom,
       fantoir,
       insee_ac,
       nom_ac
FROM   resultat;
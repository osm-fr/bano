WITH
t
AS
(SELECT fantoir,
        TRIM (BOTH FROM (COALESCE(nature_voie,'')||' '||libelle_voie)) AS nom
FROM    topo
WHERE   code_insee = '__code_insee__' AND
        caractere_annul IS NULL),
tr
AS
(SELECT  fantoir,
        nom,
        rank() OVER (PARTITION BY nom ORDER BY fantoir) rang
FROM    t)
SELECT  fantoir,
        nom
FROM    tr
WHERE   rang = 1
ORDER BY length(nom) DESC,nom;
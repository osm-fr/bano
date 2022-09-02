WITH
t
AS
(SELECT fantoir10,
        TRIM (BOTH FROM (COALESCE(nature_voie,'')||' '||libelle_voie)) AS nom
FROM    topo
WHERE   code_insee = '__code_insee__' AND
        caractere_annul IS NULL),
tr
AS
(SELECT  fantoir10,
        nom,
        rank() OVER (PARTITION BY nom ORDER BY fantoir10) rang
FROM    t)
SELECT  fantoir10,
        nom
FROM    tr
WHERE   rang = 1;
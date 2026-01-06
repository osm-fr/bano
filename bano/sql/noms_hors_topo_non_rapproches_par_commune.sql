WITH
noms_c
AS
(SELECT nom_nettoye
FROM   (SELECT nom_nettoye,nom_normalise FROM lieux_dits WHERE  code_insee = '__code_insee__') l
LEFT OUTER JOIN (SELECT TRIM (BOTH FROM (COALESCE(nature_voie,'')||' '||libelle_voie)) AS nom
	          FROM   topo
                 WHERE  code_insee = '__code_insee__' AND
                        COALESCE(caractere_annul,'x') NOT IN ('O','Q')) t
ON     nom_normalise = t.nom
WHERE  t.nom IS NULL),
noms_t
AS
(SELECT nom_collaboratif
FROM    bdtopo_voie_nommee
WHERE   code_insee = '__code_insee__' AND
        COALESCE(identifiant_voie_ban,'') = '' ),
noms_b
AS
(SELECT nom_voie
FROM    ban
WHERE   code_insee = '__code_insee__' AND
        id_fantoir IS NULL),
noms_f
AS
(SELECT nom
FROM    commune_filaire
WHERE   code_insee = '__code_insee__'),
diff
AS
(SELECT nom_voie
FROM    noms_b
UNION
SELECT  nom_nettoye
FROM    noms_c
UNION
SELECT  nom_collaboratif
FROM    noms_t
UNION
SELECT  nom
FROM    noms_f
EXCEPT
SELECT  nom
FROM   (SELECT *
	FROM   nom_fantoir
	WHERE  code_insee = '__code_insee__' AND
               source IN ('BAN','CADASTRE','BDTOPO','COMMUNE')) n
JOIN   (SELECT fantoir
	FROM   topo
	WHERE  code_insee = '__code_insee__' AND
               caractere_annul IN ('B','C','T','F')) t
USING  (fantoir))
SELECT  nom_voie,COALESCE(n.source,b.source,t.source,f.source)
FROM    diff
LEFT OUTER JOIN (SELECT nom_voie AS nom_ban,'B' as source FROM noms_b) b
ON      nom_voie = nom_ban
LEFT OUTER JOIN (SELECT nom_nettoye,'C' as source FROM noms_c) n
ON      nom_nettoye = nom_voie
LEFT OUTER JOIN (SELECT nom_collaboratif,'T' as source FROM noms_t) t
ON      nom_collaboratif = nom_voie
LEFT OUTER JOIN (SELECT nom,'F' as source FROM noms_f) f
ON      nom = nom_voie;
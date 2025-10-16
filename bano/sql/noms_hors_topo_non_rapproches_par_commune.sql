WITH
noms_c
AS
(SELECT nom_nettoye
FROM   (SELECT nom_nettoye FROM lieux_dits WHERE  code_insee = '__code_insee__') l
LEFT OUTER JOIN (SELECT TRIM (BOTH FROM (COALESCE(nature_voie,'')||' '||libelle_voie)) AS nom
	          FROM   topo
                 WHERE  code_insee = '__code_insee__' AND
                        COALESCE(caractere_annul,'x') NOT IN ('O','Q')) t
ON     nom_nettoye = t.nom
WHERE  t.nom IS NULL),
noms_t
AS
(SELECT nom_collaboratif
FROM   bdtopo_voie_nommee
WHERE  code_insee = '__code_insee__' AND
       COALESCE(identifiant_voie_ban,'') = '' ),
diff
AS
(SELECT nom_voie
FROM   ban
WHERE  code_insee = '__code_insee__' AND
       id_fantoir IS NULL
UNION
SELECT nom_nettoye
FROM   noms_c
UNION
SELECT nom_collaboratif
FROM   noms_t
EXCEPT
SELECT nom
FROM   (SELECT *
	  FROM   nom_fantoir
	  WHERE  code_insee = '__code_insee__' AND
               source IN ('BAN','CADASTRE','BDTOPO')) n
JOIN   (SELECT fantoir
	  FROM   topo
	  WHERE  code_insee = '__code_insee__' AND
	         caractere_annul IN ('B','C','T')) t
USING (fantoir))
SELECT nom_voie,COALESCE(n.source,t.source,'B')
FROM   diff
LEFT OUTER JOIN (SELECT nom_nettoye,'C' as source FROM noms_c) n
ON nom_nettoye = nom_voie
LEFT OUTER JOIN (SELECT nom_collaboratif,'T' as source FROM noms_t) t
ON nom_collaboratif = nom_voie
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
diff
AS
(SELECT nom_voie
FROM   ban
WHERE  code_insee = '__code_insee__' AND
       id_fantoir IS NULL
UNION
SELECT nom_nettoye
FROM   noms_c
EXCEPT
SELECT nom
FROM   (SELECT *
	  FROM   nom_fantoir
	  WHERE  code_insee = '__code_insee__' AND
               source IN ('BAN','CADASTRE')) n
JOIN   (SELECT fantoir
	  FROM   topo
	  WHERE  code_insee = '__code_insee__' AND
	         caractere_annul IN ('B','C')) t
USING (fantoir))
SELECT nom_voie,COALESCE(n.source,'B')
FROM   diff
LEFT OUTER JOIN (SELECT nom_nettoye,'C' as source FROM noms_c) n
ON nom_nettoye = nom_voie
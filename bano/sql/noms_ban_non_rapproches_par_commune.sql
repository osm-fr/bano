SELECT DISTINCT voie_autre
FROM   cumul_adresses c
LEFT OUTER JOIN (SELECT fantoir10 AS fantoir
	             FROM   fantoir_voie
	             WHERE  code_insee = '__code_insee__' AND
	                    caractere_annul != 'B') f
USING (fantoir)
WHERE  insee_com = '__code_insee__'AND
       source = 'BAN' AND
       (c.fantoir IS NULL OR f.fantoir IS NULL)
INTERSECT
SELECT nom_voie
FROM ban_odbl
WHERE code_insee = '__code_insee__' AND
      id_fantoir IS NULL;


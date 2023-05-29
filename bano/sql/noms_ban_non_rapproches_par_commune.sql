SELECT nom_voie
FROM   ban
WHERE  code_insee = '__code_insee__' AND
       id_fantoir IS NULL
EXCEPT
SELECT nom
FROM   (SELECT *
	  FROM   nom_fantoir
	  WHERE  code_insee = '__code_insee__' AND
               source = 'BAN')n
JOIN   (SELECT fantoir
	  FROM   topo
	  WHERE  code_insee = '__code_insee__' AND
	         caractere_annul = 'B') t
USING (fantoir);
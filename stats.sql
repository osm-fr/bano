\set dp '\'%' :dept '%\''
SELECT 		dept,
		etape,
		source,
		sum(nombre_adresses)"nb adresses"
FROM		batch
WHERE           dept like :dp
GROUP BY	1,2,3
ORDER BY	1,2 DESC,3;

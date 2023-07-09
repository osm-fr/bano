INSERT INTO bano_points_nommes (fantoir,nom,code_insee,code_dept,nature,code_insee_ancienne_commune,nom_ancienne_commune,source,lon,lat)
SELECT fantoir,
       COALESCE(nom_voie,nom_place),
	   code_insee,
	   code_dept,
	   'numero',
	   code_insee_ancienne_commune,
	   nom_ancienne_commune,
	   'OSM',
	   lon,
	   lat
FROM   (SELECT a.*,
		       RANK() OVER (PARTITION BY fantoir ORDER BY numero) rang
		FROM   (SELECT fantoir FROM bano_adresses      WHERE code_insee = '__code_insee__' AND source = 'OSM'
				EXCEPT
				SELECT fantoir from bano_points_nommes WHERE code_insee = '__code_insee__' AND source = 'OSM') f
		JOIN   (SELECT *
				FROM   bano_adresses
				WHERE  source = 'OSM' AND
					   code_insee = '__code_insee__')a
		USING (fantoir))t
WHERE rang = 1;
SELECT 	ST_AsText(ST_Transform(ST_SetSRID(geometrie,4326),900913)) geometrie,
		libelle_hameau
FROM	suffixe
WHERE	insee_com = '__com__';
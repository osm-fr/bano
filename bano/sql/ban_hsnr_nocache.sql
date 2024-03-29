WITH
j
AS
(SELECT id,
	    numero,
	    nom_voie,
	    lon,
	    lat,
	    rep,
        CASE r.numero
            WHEN b.numero THEN
		        CASE
			        WHEN rep = 'b' THEN 'bis'
			        WHEN rep = 't' THEN 'ter'
		            WHEN rep = 'q' THEN 'quater'
			        ELSE NULL
		        END
        	ELSE NULL
        END as rep_bis,
        code_postal,
        id_fantoir
FROM    ban_odbl b
LEFT OUTER JOIN rep_b_as_bis r
USING   (id_fantoir,numero)
WHERE   code_insee = '__com__')

SELECT  id,
        TRIM (BOTH FROM (numero||' '||COALESCE(rep_bis,rep,''))),
        nom_voie,
        lon,
        lat,
        code_postal,
        id_fantoir
FROM    j;

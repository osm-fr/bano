WITH
j
AS
(SELECT numero,
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
        code_insee_ancienne_commune,
        nom_ancienne_commune
FROM    ban_odbl b
LEFT OUTER JOIN rep_b_as_bis r
USING   (id_fantoir,numero)
WHERE   code_insee = '__code_insee__')
SELECT  TRIM (BOTH FROM (numero||' '||COALESCE(rep_bis,rep,''))),
        nom_voie,
        lon,
        lat,
        code_postal,
        code_insee_ancienne_commune,
        nom_ancienne_commune
FROM    j;

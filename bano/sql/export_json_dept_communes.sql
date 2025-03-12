SELECT DISTINCT i.code_insee        AS id,
                i.type              AS type,
                i.name              AS name,
                cp.cps              AS postcode,
                round(lat,6)::float AS lat,
                round(lon,6)::float AS lon,
                CASE
                    WHEN pa.libelle IS NOT NULL THEN ARRAY[pa.libelle, i.name]
                    ELSE ARRAY[i.name]
                END AS city,
                cd.libelle          AS departement,
                cr.libelle          AS region,
                population,
                adm_weight,
                GREATEST(0.075,ROUND(LOG((adm_weight)+LOG(population+1)/3)::decimal,4))::float AS importance
FROM     infos_communes i
JOIN     insee_codes_postaux cp
USING    (code_insee)
JOIN     cog_departement cd
USING    (dep)
JOIN     cog_region cr
USING    (reg)
LEFT JOIN cog_pyramide_admin AS cog ON
    cog.typecom = 'ARM' AND
    cog.code_insee = i.code_insee
LEFT JOIN cog_commune AS a ON
    cog.code_insee = a.com
LEFT JOIN cog_commune AS pa ON
    pa.com = a.comparent
WHERE    i.dep = '__dept__'
ORDER BY i.code_insee;

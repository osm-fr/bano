SELECT DISTINCT code_insee          AS id,
                i.type              AS type,
                i.name              AS name,
                cp.cps              AS postcode,
                round(lat,6)::float AS lat,
                round(lon,6)::float AS lon,
                i.name              AS city,
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
WHERE    i.dep = '__dept__'
ORDER BY code_insee;
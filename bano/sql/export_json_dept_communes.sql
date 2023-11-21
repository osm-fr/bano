WITH
rang_cp
AS
(SELECT *,
        RANK() OVER(PARTITION BY insee ORDER BY ligne_5,cp) AS rang
FROM    codes_postaux),
cp
AS
(SELECT insee AS code_insee,
        cp
FROM    rang_cp
WHERE   rang = 1)
SELECT DISTINCT code_insee AS id,    -- id
                i.type,              -- type
                i.name,              -- name
                cp.cp,               -- postcode
                round(lat,6) AS lat, -- lat
                round(lon,6) AS lon, -- lon
                i.name ,             -- city
                cd.libelle,          -- departement
                cr.libelle,          -- region,
                population,
                adm_weight,
                GREATEST(0.075,ROUND(LOG((adm_weight)+LOG(population+1)/3)::decimal,4)) AS importance
FROM     infos_communes i
JOIN     cp
USING    (code_insee)
JOIN     cog_departement cd
USING    (dep)
JOIN     cog_region cr
USING    (reg)
WHERE    i.dep = '__dept__'
ORDER BY code_insee;
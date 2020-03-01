WITH
rang_cp
AS
(SELECT *,
        RANK() OVER(PARTITION BY insee ORDER BY ligne_5,cp) AS rang
FROM    codes_postaux),
cp
AS
(SELECT insee,
       cp
FROM rang_cp
--WHERE insee in (select insee from rang where rang = 1 group by 1 having count(*) > 1)
WHERE rang = 1)
--order by 1,3
SELECT DISTINCT insee AS id, -- id
       i.type,      -- type
       i.name,      -- name
       cp.cp,       -- postcode
       round(lat,6) AS lat, -- lat
       round(lon,6) AS lon, -- lon
       i.name ,            -- city
       cd.libelle, -- departement
       cr.libelle, -- region,
        population,
        adm_weight,
        greatest(0.075,round(log((adm_weight)+log(population+1)/3)::decimal,4)) AS importance
FROM infos_communes i
JOIN cp cp
ON insee_com=insee
JOIN cog_departement cd
USING (dep)
JOIN cog_region cr
USING (reg)
WHERE insee LIKE '92%'
ORDER BY insee;
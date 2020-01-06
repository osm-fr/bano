SELECT insee AS id,
       CASE
           WHEN population<1 THEN 'village' 
           WHEN population<'10' THEN 'town' 
           ELSE 'city' 
        END  AS type,
        g.nom AS name,
        ca.code_postal AS postcode,
        round(lat_chf,6) AS lat,
        round(lon_chf,6) AS lon,
        g.nom AS city,
        cog.nom_dep AS departement,
        cog.nom_reg AS region,
        population,
        CASE
            WHEN statut LIKE 'Capital%' THEN 6
            WHEN statut = 'Préfecture de régi' THEN 5
            WHEN statut='Préfecture' THEN 4
            WHEN statut LIKE 'Sous-pr%' THEN 3
            WHEN statut='Chef-lieu canton' THEN 2
            ELSE 1
         END AS adm_weight,
         greatest(0.075,round(log((CASE
                                       WHEN statut LIKE 'Capital%' THEN 6
                                       WHEN statut = 'Préfecture de régi' THEN 5
                                       WHEN statut='Préfecture' THEN 4
                                       WHEN statut LIKE 'Sous-pr%' THEN 3
                                       WHEN statut='Chef-lieu canton' THEN 2
                                       ELSE 1
                                   END)+log(population+1)/3),4)) AS importance
FROM geofla_plus g 
JOIN code_cadastre ca
ON (ca.insee_com=insee)
JOIN (SELECT dep, nom_dep, nom_reg FROM cog GROUP BY dep,nom_dep, nom_reg) AS cog
ON (cog.dep=LEFT(insee,2) or cog.dep=LEFT(insee,3))
WHERE insee LIKE '92%'
ORDER BY insee;

-- insee
-- lat/lon admin_centre
-- pop en milliers
-- statut 
-- code postal
-- dep
-- nom dep
-- nom reg

WITH
duplicates
AS
(SELECT fantoir,
        nom_voie,
        code_insee_ancienne_commune,
        nom_ancienne_commune,
        lon,
        lat,
        RANK() OVER (PARTITION BY nom_voie ORDER BY numero) rang
FROM    (SELECT fantoir,numero,nom_voie,code_insee,code_insee_ancienne_commune,nom_ancienne_commune,lon,lat
        FROM    ban
        WHERE   code_insee = '__code_insee__'
        ) AS ban)
SELECT  lon,
        lat,
        nom_voie,
        code_insee_ancienne_commune,
        fantoir,
        nom_ancienne_commune
FROM    duplicates
WHERE   rang = 1;

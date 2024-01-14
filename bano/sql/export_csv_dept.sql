SELECT  id_add      AS id,
        numero,
        nom_voie    AS voie,
        code_postal AS code_post,
        libelle     AS ville,
        source,
        lat,
        lon,
        geometrie   AS geom
FROM    numeros_export
WHERE   dep = '__dept__'
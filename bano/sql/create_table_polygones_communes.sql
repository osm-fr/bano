CREATE TABLE IF NOT EXISTS polygones_insee (
        geometrie geometry (Geometry, 4326),
        code_insee character(5),
        nom text,
        admin_level integer);
CREATE INDEX IF NOT EXISTS gidx_polygones_insee ON polygones_insee USING GIST (geometrie);
CREATE INDEX IF NOT EXISTS idx_polygones_insee_code_insee ON polygones_insee(code_insee);

TRUNCATE TABLE polygones_insee;
INSERT INTO polygones_insee
SELECT way,
       "ref:INSEE",
       name,
       admin_level
FROM planet_osm_polygon
WHERE boundary='administrative' AND
      admin_level in (8,9) AND
      name != '';

CREATE TABLE IF NOT EXISTS polygones_insee_a9 (
        geometrie geometry (Geometry, 4326),
        code_insee character(5),
        nom text,
        insee_a8 character(5));
CREATE INDEX IF NOT EXISTS gidx_polygones_insee_a9 ON polygones_insee_a9 USING GIST (geometrie);
CREATE INDEX IF NOT EXISTS idx_polygones_insee_a9_code_insee ON polygones_insee_a9(code_insee);
CREATE INDEX IF NOT EXISTS idx_polygones_insee_a9_insee_a8 ON polygones_insee_a9(insee_a8);

TRUNCATE TABLE polygones_insee_a9;
INSERT INTO polygones_insee_a9
SELECT a9.geometrie,
       a9.code_insee,
       a9.nom,
       a8.code_insee
FROM   (SELECT * FROM polygones_insee WHERE admin_level = 9) a9
JOIN   (SELECT * FROM polygones_insee WHERE admin_level = 8) a8
ON     ST_Contains(a8.geometrie,a9.geometrie);

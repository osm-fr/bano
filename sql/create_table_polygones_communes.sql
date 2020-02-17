CREATE TABLE IF NOT EXISTS polygones_insee (
        geometrie geometry (Geometry, 3857),
        insee_com character(5),
        nom text,
        admin_level integer);
CREATE INDEX IF NOT EXISTS gidx_polygones_insee ON polygones_insee USING GIST (geometrie);
CREATE INDEX IF NOT EXISTS idx_population_insee_insee_com ON polygones_insee(insee_com);

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

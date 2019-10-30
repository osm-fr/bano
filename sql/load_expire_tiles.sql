TRUNCATE expire_tiles;
COPY expire_tiles(z,x,y) FROM '/data/project/bano_data/expire_tiles/20190930/211505.316.tiles' WITH CSV DELIMITER '/';

UPDATE expire_tiles
SET    geometrie = ST_SetSRID(ST_MakeBox2D(ST_Point(-20037508.34 + (40075016.68/(2 ^ :zoom)) *  x, 20037508.34 - (40075016.68/(2 ^ :zoom)) *  y),
    ST_Point( -20037508.34 + (40075016.68/(2 ^ :zoom)) * (x + 1) ,20037508.34 - (40075016.68/(2 ^ :zoom)) * (y + 1))),3857)

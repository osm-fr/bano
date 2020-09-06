ALTER TABLE ban_odbl ADD COLUMN geometrie geometry(Point, 4326);
UPDATE ban_odbl SET geometrie = ST_SetSRID(ST_Point(lon,lat),4326);
CREATE INDEX gidx_ban_odbl ON ban_odbl USING GIST(geometrie);
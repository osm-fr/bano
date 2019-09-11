CREATE INDEX idx_planet_osm_polygon_ref_insee ON planet_osm_polygon("ref:INSEE");
CREATE INDEX idx_planet_osm_rels_id ON planet_osm_rels(osm_id);

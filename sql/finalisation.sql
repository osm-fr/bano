CREATE INDEX idx_planet_osm_point_fantoir ON             planet_osm_point("ref:FR:FANTOIR");
CREATE INDEX idx_planet_osm_point_housenumber ON         planet_osm_point("addr:housenumber");
CREATE INDEX idx_planet_osm_line_fantoir ON              planet_osm_line("ref:FR:FANTOIR");
CREATE INDEX idx_planet_osm_polygon_fantoir ON           planet_osm_polygon("ref:FR:FANTOIR");
CREATE INDEX idx_planet_osm_polygon_housenumber ON       planet_osm_polygon("addr:housenumber");
CREATE INDEX idx_planet_osm_polygon_ref_insee ON         planet_osm_polygon("ref:INSEE");
CREATE INDEX idx_planet_osm_rels_id ON                   planet_osm_rels(osm_id);
CREATE INDEX idx_planet_osm_communes_statut_ref_insee ON planet_osm_communes_statut("ref:INSEE");

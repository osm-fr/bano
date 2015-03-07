# extraction limites des codes postaux vers shapefile
ogr2ogr -f "ESRI Shapefile" -lco ENCODING=UTF-8 -s_srs EPSG:900913 -t_srs "EPSG:4326" -overwrite postal_code.shp \
	PG:"host=osm105.openstreetmap.fr user=cadastre password=b4n0 dbname=osm" \
	-sql "select cp.way, c.tags->'ref:INSEE' as insee, cp.tags->'postal_code' as postal_cod, coalesce(cp.tags->'postal_code:name',cp.tags->'addr:postcode:name') as nom from planet_osm_polygon r join planet_osm_polygon cp on (cp.boundary='postal_code' and cp.tags ? 'postal_code' and ST_Contains(r.way,cp.way)) left join planet_osm_polygon c on (c.tags ? 'ref:INSEE' and c.admin_level='8' and ST_Contains(c.way, st_centroid(cp.way))) where r.tags ? 'ref:INSEE' and r.admin_level='4';"

# mise à jour base BANO
ogr2ogr -f PostgreSQL PG:dbname=cadastre postal_code.shp -overwrite -nlt GEOMETRY -nln postal_code

# suppression colonne inutile et création index sur le code INSEE
psql cadastre -c "alter table postal_code drop column ogc_fid; create index postal_code_insee on postal_code (insee);"


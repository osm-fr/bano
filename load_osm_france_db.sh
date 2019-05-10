source config
cd /data/download
rm -rf france_metro_dom_com_nc.osm.pbf
wget http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf
/app/imposm/imposm import -mapping $BANO_DIR/bano.yml -read /data/download/france_metro_dom_com_nc.osm.pbf -overwritecache -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff
/app/imposm/imposm import -mapping $BANO_DIR/bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir /data/bano_imposm_cache -dbschema-import public -diff -diffdir /data/bano_imposm_diff

psql -d osm -U cadastre -f $BANO_DIR/sql/finalisation.sql

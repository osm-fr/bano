# wget http://download.openstreetmap.fr/extracts/merge/france_metro_dom_com_nc.osm.pbf
/app/imposm/imposm import -mapping ./bano.yml -read /data/download/france_metro_dom_com_nc.osm.pbf -overwritecache -cachedir /data/bano_imposm_cachedir -dbschema-import public -diff -diffdir /data/bano_imposm_diffdir
/app/imposm/imposm import -mapping ./bano.yml -write -connection 'postgis://cadastre@localhost/osm'?prefix=NONE -cachedir /data/bano_imposm_cachedir -dbschema-import public -diff -diffdir /data/bano_imposm_diffdir

psql -d osm -U cadastre -f sql/finalisation.sql
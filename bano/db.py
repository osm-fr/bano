import os

import psycopg2
import psycopg2.extras

bano = psycopg2.connect(os.environ.get("PG_CADASTRE", "dbname='cadastre' user='cadastre'"))
bano_cache = psycopg2.connect(os.environ.get("PG_OSM", "dbname='osm' user='cadastre'"))
bano_cache.autocommit = True
psycopg2.extras.register_hstore(bano_cache)

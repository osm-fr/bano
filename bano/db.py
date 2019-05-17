import os

import psycopg2

bano = psycopg2.connect(os.environ.get("BANO_PG", "dbname='cadastre' user='cadastre'"))
bano_cache = psycopg2.connect(os.environ.get("BANO_PG_CACHE", "dbname='osm' user='cadastre'"))

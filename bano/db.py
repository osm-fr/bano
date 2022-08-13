import os

import psycopg2
import psycopg2.extras

# bano = psycopg2.connect(os.environ.get("BANO_PG", "dbname='cadastre' user='cadastre'"))
bano_sources = psycopg2.connect(os.environ.get("BANO_PG_CACHE", "dbname='bano_sources' user='cadastre'"))
# psycopg2.extras.register_hstore(bano_cache)

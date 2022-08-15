import os

import psycopg2
import psycopg2.extras

bano = psycopg2.connect(os.environ.get("BANO_PG", "dbname='bano' user='cadastre'"))
bano.autocommit = True
bano_sources = psycopg2.connect(os.environ.get("BANO_PG_CACHE", "dbname='bano_sources' user='cadastre'"))
bano_sources.autocommit = True
# psycopg2.extras.register_hstore(bano_cache)

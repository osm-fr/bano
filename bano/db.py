import os

import psycopg2
import psycopg2.extras

bano_db = psycopg2.connect(os.environ.get("PG_BANO"))
bano_db.autocommit = True
psycopg2.extras.register_hstore(bano_db)

import os

import psycopg2

def get_pgc():
	pgc = psycopg2.connect(os.environ.get("BANO_PG", "dbname='cadastre' user='cadastre'"))
	return pgc

def get_pgc_osm():
    pgc = psycopg2.connect(os.environ.get("BANO_PG_CACHE", "dbname='osm' user='cadastre'"))
    return pgc

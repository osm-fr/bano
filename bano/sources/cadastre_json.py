import csv
import gzip
import json
import os
import subprocess
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests
import psycopg2

from ..constants import DEPARTEMENTS
from .. import db
from .. import helpers as hp


def process(prefixe, departements, **kwargs):
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    for dept in sorted(departements):
        print(f"Processing {dept}")
        status = download(prefixe, dept)
        if status:
            import_to_pg(prefixe, dept)
            post_process(prefixe, dept)
    

def download(prefixe, departement):
    destination = get_destination(prefixe, departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/{departement}/cadastre-{departement}-{prefixe}.json.gz', headers=headers)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        return True
    return False


def import_to_pg(prefixe, departement, **kwargs):
    fichier_source = get_destination(prefixe, departement)
    with gzip.open(fichier_source, mode='rt') as f:
        json_source = json.load(f)
        with  db.bano_cache.cursor() as cur_insert:
            try:
                cur_insert.execute(f"DELETE FROM {prefixe} WHERE insee_com LIKE '{departement+'%'}';COMMIT;")
                a_values = []
                str_query = f"INSERT INTO {prefixe} VALUES "
                for l in json_source['features']:
                    a_values.append(f"('{l['properties']['commune']}','{hp.escape_quotes(l['properties']['nom'])}','{l['properties']['created']}','{l['properties']['updated']}',ST_SetSRID(ST_GeomFromGeoJSON('{hp.replace_single_quotes_with_double(str(l['geometry']))}'),4326))")
                if a_values:
                    cur_insert.execute(str_query+','.join(a_values)+';COMMIT;')
            except psycopg2.DataError as e:
                print(e)
                db.bano_cache.reset()
    
def post_process(prefixe, departement, **kwargs):
    sqlfile = Path(__file__).parent.parent / 'sql' / f'{prefixe}_post_process.sql'
    if sqlfile.exists():
        with open(sqlfile,'r') as fq:
            with  db.bano_cache.cursor() as cur_post_process:
                str_query = fq.read().replace('__dept__',departement)
                cur_post_process.execute(str_query)
    
def get_destination(prefixe, departement):
    try:
        cwd = Path(os.environ['CADASTRE_CACHE_DIR'])
    except KeyError:
        raise ValueError(f"La variable CADASTRE_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'cadastre-{departement}-{prefixe}.json.gz'

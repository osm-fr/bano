# import csv
from zipfile import ZipFile
import os
# import subprocess
# from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests
# import psycopg2

from ..db import bano_db
from ..sql import sql_process
from .. import batch as b

def process_cog(**kwargs):
    sql_process('create_table_cog',dict(),bano_db)
    zip = get_destination('cog_2022.zip')
    status = download(zip)
    if status:
        import_to_pg(zip)

def download(destination):
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://www.insee.fr/fr/statistiques/fichier/6051727/cog_ensemble_2022_csv.zip', headers=headers)
    id_batch = b.batch_start_log('download source', 'COG ZIP','France')
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        # mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        # os.utime(destination, (mtime, mtime))
        b.batch_stop_log(id_batch,True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch,False)
    return False


def import_to_pg(fichier_zip):
    table = 'cog_commune'
    id_batch = b.batch_start_log('import source', f'COG {table}','France')
    with ZipFile(fichier_zip) as f:
        with f.open('commune_2022.csv') as csv:
            csv.readline()  # skip CSV headers
            with bano_db.cursor() as cur_insert:
                try:
                    cur_insert.execute(f"TRUNCATE {table}")
                    cur_insert.copy_from(csv,table, sep=',', null='')
                    b.batch_stop_log(id_batch,True)
                except psycopg2.DataError as e:
                    b.batch_stop_log(id_batch,False)
    
def get_destination(fichier_cog):
    try:
        cwd = Path(os.environ['COG_DIR'])
    except KeyError:
        raise ValueError(f"La variable COG_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'{fichier_cog}'

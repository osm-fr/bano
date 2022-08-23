# import csv
# import gzip
import os
# import subprocess
# from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests
# import psycopg2

from ..db import bano
from ..sql import sql_process
from .. import batch as b
# from .. import update_manager as um

def process_cog(**kwargs):
    sql_process('create_table_cog',dict(),bano)
    for fichier_cog in ['cog_commune']:
        status = download(fichier_cog)
        if status:
            import_to_pg(fichier_cog)

def download(fichier_cog):
    destination = get_destination(fichier_cog)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://www.data.gouv.fr/fr/datasets/r/6c1db35c-3ee3-42f8-80fb-d366e451cc30', headers=headers)
    id_batch = b.batch_start_log('download source', 'COG commune','France')
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


def import_to_pg(fichier_cog):
    id_batch = b.batch_start_log('import source', f'COG {fichier_cog}','France')
    fichier_source = get_destination(fichier_cog)
    with open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        with bano.cursor() as cur_insert:
            try:
                cur_insert.execute(f"TRUNCATE {fichier_cog}")
                cur_insert.copy_from(f,fichier_cog, sep=',', null='')
                b.batch_stop_log(id_batch,True)
            except psycopg2.DataError as e:
                b.batch_stop_log(id_batch,False)
    
def get_destination(fichier_cog):
    try:
        cwd = Path(os.environ['CSV_DIR'])
    except KeyError:
        raise ValueError(f"La variable CSV n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'{fichier_cog}.csv'

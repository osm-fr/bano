import csv
import gzip
import os
import subprocess
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests
import psycopg2

from ..constants import DEPARTEMENTS
from .. import db
from .. import db_helpers as dbh
from .. import outils_de_gestion as m
from .. import update_manager as um

def process(departements, **kwargs):
    source = 'BAN'
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    um.set_csv_directory(um.get_directory_pathname())
    for dept in sorted(departements):
        print(f"Processing {dept}")
        status = download(source, dept)
        if status:
            import_to_pg(source, dept)

def download(source, departement):
    destination = get_destination(departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://adresse.data.gouv.fr/data/ban/adresses-odbl/latest/csv/adresses-{departement}.csv.gz', headers=headers)
    if resp.status_code == 200:
        batch_id = m.batch_start_log(source,'downloadDeptBan',departement)
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        m.batch_end_log(-1,batch_id)
        return True
    print(resp.status_code)
    return False


def import_to_pg(source, departement, **kwargs):
    batch_id = m.batch_start_log(source,'loadDeptBal',departement)
    fichier_source = get_destination(departement)
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        with  db.bano_cache.cursor() as cur_insert:
            try:
                cur_insert.execute(f"DELETE FROM ban_odbl WHERE code_insee LIKE '{departement+'%'}'")
                cur_insert.copy_from(f, "ban_odbl", sep=';', null='')
                db.bano_cache.commit()
                # um.save_bal_insee_list(um.get_directory_pathname(),departement)
            except psycopg2.DataError as e:
                db.bano_cache.reset()
    m.batch_end_log(-1,batch_id)

    
def get_destination(departement):
    try:
        cwd = Path(os.environ['BAN_CACHE_DIR'])
    except KeyError:
        raise ValueError(f"La variable BAN_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'adresses-{departement}.csv.gz'

def update_bis_table(**kwargs):
    dbh.process_sql(db.bano_cache,'update_table_rep_b_as_bis',dict())
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
from ..db import bano_sources
from ..sql import sql_process
from .. import batch as b
# from .. import update_manager as um

def process_ban(departements, **kwargs):
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    depts_en_echec = []
    for dept in sorted(departements):
        print(f"Département {dept}")
        status = download(dept)
        if status:
            if not (import_to_pg(dept)):
                depts_en_echec.append(dept)
                print('depts_en_echec',depts_en_echec)

    for dept in depts_en_echec:
        print(f"Département {dept}")
        import_to_pg_subp(dept)


def download(departement):
    destination = get_destination(departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://adresse.data.gouv.fr/data/ban/adresses-odbl/latest/csv/adresses-{departement}.csv.gz', headers=headers)
    id_batch = b.batch_start_log('download source', 'BAN',departement)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        b.batch_stop_log(id_batch,True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch,False)
    return False

def import_to_pg(departement, **kwargs):
    id_batch = b.batch_start_log('import source', 'BAN',departement)
    fichier_source = get_destination(departement)
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        with  bano_sources.cursor() as cur_insert:
            try:
                cur_insert.execute(f"DELETE FROM ban WHERE code_insee LIKE '{departement}%'")
                cur_insert.copy_from(f, "ban", sep=';', null='')
                b.batch_stop_log(id_batch,True)
                return True
            except psycopg2.DataError as e:
                print(f"Erreur au chargement de la BAN {departement}")
                print(e)
                return False

def import_to_pg_subp(departement, **kwargs):
    id_batch = b.batch_start_log('import source', 'BAN',departement)
    print("Essai via shell")
    try:
        fichier_source = get_destination(departement)
        ret = subprocess.run(["gzip","-cd",fichier_source],capture_output=True,text=True)
        tmp_filename = Path(os.environ['BAN_CACHE_DIR']) / 'tmp.csv'
        with open(tmp_filename,'w') as tmpfile:
            tmpfile.write(ret.stdout)

        subprocess.run(["psql","-d","bano_sources","-U","cadastre","-1","-c",f"DELETE FROM ban WHERE code_insee LIKE '{departement}%';COPY ban FROM '{tmp_filename}' WITH CSV HEADER NULL '' DELIMITER ';'"])
        tmp_filename.unlink()
        b.batch_stop_log(id_batch,True)
    except e:
        print(f"Erreur au chargement de la BAN {departement}")
        print(f"Abandon du chargement de la BAN {departement}")
        b.batch_stop_log(id_batch,False)
    
def get_destination(departement):
    try:
        cwd = Path(os.environ['BAN_CACHE_DIR'])
    except KeyError:
        raise ValueError(f"La variable BAN_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'adresses-{departement}.csv.gz'

def update_bis_table(**kwargs):
    sql_process('update_table_rep_b_as_bis',dict(),bano_sources)
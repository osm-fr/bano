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
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    um.set_csv_directory(um.get_directory_pathname())
    depts_en_echec = []
    for dept in sorted(departements):
        print(f"Processing {dept}")
        status = download(dept)
        if status:
            if not (import_to_pg(dept)):
                depts_en_echec.append(dept)

    for dept in depts_en_echec:
        print(f"Département {dept}")
        import_to_pg_subp(dept)

def download(departement):
    destination = get_destination(departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://adresse.data.gouv.fr/data/ban/adresses-odbl/latest/csv/adresses-{departement}.csv.gz', headers=headers)
    if resp.status_code == 200:
        batch_id = m.batch_start_log('BAN','downloadDeptBan',departement)
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        m.batch_end_log(-1,batch_id)
        return True
    print(resp.status_code)
    return False


def import_to_pg( departement, **kwargs):
    batch_id = m.batch_start_log('BAN','loadDeptBal',departement)
    fichier_source = get_destination(departement)
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        with  db.bano_cache.cursor() as cur_insert:
            try:
                cur_insert.execute(f"DELETE FROM ban_odbl WHERE code_insee LIKE '{departement}%'")
                cur_insert.copy_from(f, "ban_odbl", sep=';', null='')
                db.bano_cache.commit()
                m.batch_end_log(-1,batch_id)
                return True
            except psycopg2.DataError as e:
                print(f"Erreur au chargement de la BAN {departement}")
                print(e)
                m.batch_end_log(-1,batch_id)
                cur_insert.close()
                return False

def import_to_pg_subp(departement, **kwargs):
    batch_id = m.batch_start_log('BAN','loadDeptBal',departement)
    print("Essai via shell")
    try:
        fichier_source = get_destination(departement)
        ret = subprocess.run(["gzip","-cd",fichier_source],capture_output=True,text=True)
        tmp_filename = Path(os.environ['BAN_CACHE_DIR']) / 'tmp.csv'
        with open(tmp_filename,'w') as tmpfile:
            tmpfile.write(ret.stdout)

        subprocess.run(["psql","-d","osm","-U","cadastre","-1","-c",f"DELETE FROM ban_odbl WHERE code_insee LIKE '{departement}%';COPY ban_odbl FROM '{tmp_filename}' WITH CSV HEADER NULL '' DELIMITER ';'"])
        tmp_filename.unlink()
        m.batch_end_log(-1,batch_id)
    except e:
        print(f"Erreur au chargement de la BAN {departement}")
        print(f"Abandon du chargement de la BAN {departement}")
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
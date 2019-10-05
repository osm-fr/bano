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


def process(source, departements, **kwargs):
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    if source == 'CADASTRE':
        suffixe_fichier = 'cadastre'
    else:
        suffixe_fichier = 'locales'
    for dept in sorted(departements):
        print(f"Processing {dept}")
        status = download(suffixe_fichier, dept)
        if status:
            import_to_pg(suffixe_fichier, dept)
    

def download(suffixe_fichier, departement):
    destination = get_destination(suffixe_fichier, departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://adresse.data.gouv.fr/data/adresses-{suffixe_fichier}/latest/csv/adresses-{suffixe_fichier}-{departement}.csv.gz', headers=headers)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        return True
    return False


def import_to_pg(suffixe_fichier, departement, **kwargs):
    fichier_source = get_destination(suffixe_fichier, departement)
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        with  db.bano_cache.cursor() as cur_insert:
            try:
                cur_insert.execute(f"DELETE FROM bal_{suffixe_fichier} WHERE commune_code LIKE '{departement+'%'}'")
                cur_insert.copy_from(f, f"bal_{suffixe_fichier}", sep=';', null='')
                db.bano_cache.commit()
            except psycopg2.DataError as e:
                db.bano_cache.reset()
    
    
def get_destination(suffixe_fichier, departement):
    try:
        cwd = Path(os.environ['BAL_CACHE_DIR'])
    except KeyError:
        raise ValueError(f"La variable BAL_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'adresses-{suffixe_fichier}-{departement}.csv.gz'

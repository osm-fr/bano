import csv
import gzip
import os
import subprocess
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests

from ..constants import DEPARTEMENTS
from ..pg_connexion import get_pgc_osm


def process(source, departements, **kwargs):
    departements = set(departements)
    depts_inconnus =  departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    for dept in departements:
        status = download(source, dept)
        if status:
            import_to_pg(source, dept)
    

def download(source, departement):
    destination = get_destination(source, departement)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://adresse.data.gouv.fr/data/adresses-locales/latest/csv/adresses-locales-{departement}.csv.gz', headers=headers)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers['Last-Modified']).timestamp()
        os.utime(destination, (mtime, mtime))
        return True
    return False


def import_to_pg(source, departement, **kwargs):
    fichier_source = get_destination(source, departement)
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        conn = get_pgc_osm()
        with  conn.cursor() as cur_insert:
            cur_insert.execute("DELETE FROM bal_locales WHERE commune_code LIKE %s", (departement+'%',))
            cur_insert.copy_from(f, 'bal_locales', sep=';')
            conn.commit()
    
    
def get_destination(source, departement):
    try:
        cwd = Path(os.environ['BAL_CACHE_DIR'])
    except KeyError:
        raise ValueError(f"La variable BAL_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f'adresses-locales-{departement}.csv.gz'

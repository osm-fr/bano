#!/usr/bin/env python

import os
from pathlib import Path
from email.utils import formatdate, parsedate_to_datetime
# import time

# from bs4 import BeautifulSoup
import requests

from .. import outils_de_gestion as m
from .. import db


def dowload():
    destination = get_destination()
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://plateforme.adresse.data.gouv.fr/api/communes-summary.csv', headers=headers)
    if resp.status_code == 200:
        batch_id = m.batch_start_log('datagouv','downloadCommuneSummary','FRA')
        with destination.open('wb') as f:
            f.write(resp.content)
        m.batch_end_log(-1,batch_id)
        return True
    print(resp.status_code)
    return False


def update_table_in_db():
    with open(get_destination()) as csv:
        csv.readline()
        with db.bano.cursor() as cur:
            cur.execute("TRUNCATE communes_summary;COMMIT;")
            cur.copy_from(csv,'communes_summary',sep=',',null='')

def get_destination():
    return Path(os.environ['BAN_CACHE_DIR']) / 'communes-summary.csv'

def process(**kwargs):
    if dowload():
        update_table_in_db()

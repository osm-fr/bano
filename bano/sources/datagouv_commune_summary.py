#!/usr/bin/env python

import os
import requests

from pathlib import Path
from email.utils import formatdate, parsedate_to_datetime

from .. import batch as b
from ..db import bano_db

def dowload():
    destination = get_destination()
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    resp = requests.get(f'https://plateforme.adresse.data.gouv.fr/api/communes-summary.csv', headers=headers)
    if resp.status_code == 200:
        id_batch = b.batch_start_log("download source", "CommuneSummary", 'FRA')
        with destination.open('wb') as f:
            f.write(resp.content)
        b.batch_stop_log(id_batch, True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def update_table_in_db():
    with open(get_destination()) as csv:
        csv.readline()
        with bano_db.cursor() as cur:
            cur.execute("TRUNCATE communes_summary;")
            cur.copy_from(csv,'communes_summary',sep=',',null='')

def get_destination():
    return Path(os.environ['BAN_CACHE_DIR']) / 'communes-summary.csv'

def process(**kwargs):
    if dowload():
        update_table_in_db()

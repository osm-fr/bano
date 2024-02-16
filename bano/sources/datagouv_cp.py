import os

from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests

from ..db import bano_db
from ..sql import sql_process
from .. import batch as b

DICT_SOURCES = {
    "codes_postaux": [
        "codes_postaux",
        "https://datanova.laposte.fr/data-fair/api/v1/datasets/laposte-hexasmal/raw", 
        "table_insee_codes_postaux",
    ],
}


def process(**kwargs):
    for k,v in DICT_SOURCES.items():
        print(f"Chargement de la source {k}")
        table,url,script_post_process = v
        csv = get_destination(f"{k}.csv")
        status = download(csv,url)
        if status:
            import_to_pg(csv,table)
        sql_process(script_post_process,dict())


def download(destination,url):
    headers = {}
    if destination.exists():
        headers["If-Modified-Since"] = formatdate(destination.stat().st_mtime)

    resp = requests.get(url, headers=headers)
    id_batch = b.batch_start_log("download source", url, "France")
    if resp.status_code == 200:
        with destination.open("w") as f:
            f.write(resp.text)
        b.batch_stop_log(id_batch, True)
        return True
    elif resp.status_code == 304:  # Not Modified
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def import_to_pg(csv,table):
    id_batch = b.batch_start_log("import source", table, "France")
    with open(csv) as f:
        f.readline()
        with bano_db.cursor() as cur_insert:
            try:
                cur_insert.execute(f"TRUNCATE {table}")
                cur_insert.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER DELIMITER ';'",f)
                b.batch_stop_log(id_batch, True)
            except psycopg2.DataError as e:
                b.batch_stop_log(id_batch, False)

def get_destination(fichier):
    try:
        cwd = Path(os.environ["DATA_DIR"])
    except KeyError:
        raise ValueError(f"La variable DATA_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f"{fichier}"

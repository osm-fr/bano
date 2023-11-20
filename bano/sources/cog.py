import os

from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests

from ..db import bano_db
from .. import batch as b

DICT_COG = {
    "commune": [
        "cog_commune",
        "https://www.data.gouv.fr/fr/datasets/r/5d5c4384-b19a-4ddf-910b-6e9cbaa8e1d6",
    ],
    "canton": [
        "cog_canton",
        "https://www.data.gouv.fr/fr/datasets/r/716922e8-2ab7-4806-94eb-21933c266ebf",
    ],
    "arrondissement": [
        "cog_arrondissement",
        "https://www.data.gouv.fr/fr/datasets/r/9fdf41d6-2452-4f7c-a1e2-a7b104b38b77",
    ],
    "departement": [
        "cog_departement",
        "https://www.data.gouv.fr/fr/datasets/r/c691a0b0-6e22-4d6f-9496-3406b017d709",
    ],
    "region": [
        "cog_region",
        "https://www.data.gouv.fr/fr/datasets/r/6e40e6f3-7735-43a9-8f20-ce0ae53f74f7",
    ],
}


def process_cog(**kwargs):
    for k,v in DICT_COG.items():
        print(f"Chargement de la source COG {k}")
        table,url = v
        csv = get_destination(f"{k}.csv")
        status = download(csv,url)
        if status:
            import_to_pg(csv,table)


def download(destination,url):
    headers = {}
    if destination.exists():
        headers["If-Modified-Since"] = formatdate(destination.stat().st_mtime)

    resp = requests.get(url, headers=headers)
    id_batch = b.batch_start_log("download source", f"COG {destination}", "France")
    if resp.status_code == 200:
        with destination.open("wb") as f:
            f.write(resp.content)
        b.batch_stop_log(id_batch, True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def import_to_pg(csv,table):
    id_batch = b.batch_start_log("import source", f"COG {table}", "France")
    with open(csv) as f:
        with bano_db.cursor() as cur_insert:
            try:
                cur_insert.execute(f"TRUNCATE {table}")
                cur_insert.copy_expert(f"COPY {table} FROM STDIN WITH CSV HEADER",f)
                b.batch_stop_log(id_batch, True)
            except psycopg2.DataError as e:
                b.batch_stop_log(id_batch, False)

def get_destination(fichier_cog):
    try:
        cwd = Path(os.environ["COG_DIR"])
    except KeyError:
        raise ValueError(f"La variable COG_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f"{fichier_cog}"

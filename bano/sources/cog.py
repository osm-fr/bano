import os

from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests

from ..db import bano_db
from ..sql import sql_process
from .. import batch as b

DICT_COG = {
    "commune": [
        "cog_commune",
        "https://www.data.gouv.fr/fr/datasets/r/91a95bee-c7c8-45f9-a8aa-f14cc4697545",
    ],
    "canton": [
        "cog_canton",
        "https://www.data.gouv.fr/fr/datasets/r/58c109f6-b15c-4d87-bada-6a55ba9ef7d3",
    ],
    "arrondissement": [
        "cog_arrondissement",
        "https://www.data.gouv.fr/fr/datasets/r/e3bd015d-7593-4bc5-a236-8410167e4599",
    ],
    "departement": [
        "cog_departement",
        "https://www.data.gouv.fr/fr/datasets/r/54a8263d-6e2d-48d5-b214-aa17cc13f7a0",
    ],
    "region": [
        "cog_region",
        "https://www.data.gouv.fr/fr/datasets/r/2486b351-5d85-4e1a-8d12-5df082c75104",
    ],
}


def process_cog(forceload, **kwargs):
    for k,v in DICT_COG.items():
        print(f"Chargement de la source COG {k}")
        table,url = v
        csv = get_destination(f"{k}.csv")
        status = download(csv,url)
        if status or forceload:
            import_to_pg(csv,table)
    sql_process('cog_pyramide_admin',dict())

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

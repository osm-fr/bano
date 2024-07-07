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
        "https://www.data.gouv.fr/fr/datasets/r/8262de72-138f-4596-ad2f-10079e5f4d7c",
    ],
    "canton": [
        "cog_canton",
        "https://www.data.gouv.fr/fr/datasets/r/56be3980-13c1-4c04-91fd-60dc92e8ceb8",
    ],
    "arrondissement": [
        "cog_arrondissement",
        "https://www.data.gouv.fr/fr/datasets/r/21fdff26-33a9-4b8e-bfd9-ce6d2ed5659e",
    ],
    "departement": [
        "cog_departement",
        "https://www.data.gouv.fr/fr/datasets/r/e436f772-b05d-47f8-b246-265faab8679f",
    ],
    "region": [
        "cog_region",
        "https://www.data.gouv.fr/fr/datasets/r/53cb77ce-8a93-4924-9d5d-920bbe7c679f",
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

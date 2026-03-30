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
        "https://www.data.gouv.fr/api/1/datasets/r/c5800591-813b-4ce2-9a3f-739a9c5d9558",
    ],
    "canton": [
        "cog_canton",
        "https://www.data.gouv.fr/api/1/datasets/r/3fe51f74-7185-4782-9f57-339fc1d99b99",
    ],
    "arrondissement": [
        "cog_arrondissement",
        "https://www.data.gouv.fr/api/1/datasets/r/33393ce2-6b46-4354-b41f-17722423dd15",
    ],
    "departement": [
        "cog_departement",
        "https://www.data.gouv.fr/api/1/datasets/r/e5f32177-5841-4a46-9c17-f8ff94bd38fc",
    ],
    "region": [
        "cog_region",
        "https://www.data.gouv.fr/api/1/datasets/r/f7057d4e-0078-45de-95b7-2a0ce6594807",
    ],
    "commune_comtom": [
        "cog_commune_comtom",
        "https://www.data.gouv.fr/api/1/datasets/r/f47969be-310d-4871-b6c4-6005dbf46a00",
    ],
    "collectivite_comtom": [
        "cog_collectivite_comtom",
        "https://www.data.gouv.fr/api/1/datasets/r/62cf1ca1-f3db-4f49-bfa1-69aca93d34f1",
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
    sql_process('cog_complement_comtom',dict())
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

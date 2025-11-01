import os

from email.utils import formatdate, parsedate_to_datetime

from pathlib import Path
import subprocess

import requests

# import psycopg2

# from ..db import bano_db
from ..sql import sql_process

from .. import batch as b

DICT_SOURCES = {
    "commune_filaire.json": [
        "commune_filaire",
        "https://base-adresse-locale-prod-filaires-de-voie.s3.fr-par.scw.cloud/export-filaires-de-voie.json",
        "post_chargement_commune_filaire",
    ],
}


def process(forceload, **kwargs):
    for k, v in DICT_SOURCES.items():
        print(f"Chargement de la source {k}")
        table, url, script_post_process = v
        fdest = get_destination(k)
        status = download(fdest, url, forceload)
        if status or forceload:
            import_to_pg(fdest, table)
        else:
            print("Pas de rechargement en base")
        if script_post_process:
            sql_process(script_post_process, dict())


def download(destination, url, forceload):
    headers = {}
    if destination.exists():
        headers["If-Modified-Since"] = formatdate(destination.stat().st_mtime)

    resp = requests.get(url, headers=headers)
    id_batch = b.batch_start_log("download source", url, "France")
    if resp.status_code == 200:
        with destination.open("wb") as f:
            f.write(resp.content)
        b.batch_stop_log(id_batch, True)
        return True
    elif resp.status_code == 304 and forceload:  # Not Modified
        print("Pas de nouveau téléchargement")
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def import_to_pg(fdest, table):
    print("Chargement en base")
    id_batch = b.batch_start_log("import source", table, "France")

    try:
        sql_process("drop_cascade",dict(table=table))
        subprocess.run(
            [
                "ogr2ogr",
                "-f",
                "PostgreSQL",
                "PG:" + os.environ["PG_BANO"],
                "-s_srs",
                "EPSG:4326",
                "-t_srs",
                "EPSG:4326",
                "-lco",
                "GEOMETRY_NAME=geometrie",
                "-overwrite",
                "-nln",
                table,
                fdest,
            ]
        )
        b.batch_stop_log(id_batch, True)
    except psycopg2.DataError as e:
        b.batch_stop_log(id_batch, False)


def get_destination(fichier):
    try:
        cwd = Path(os.environ["DOWNLOAD_DIR"])
    except KeyError:
        raise ValueError(f"La variable DOWNLOAD_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f"{fichier}"

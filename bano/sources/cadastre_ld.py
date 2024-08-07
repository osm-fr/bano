import csv
import gzip
import json
import os
import subprocess
from datetime import datetime
from email.utils import formatdate, parsedate_to_datetime
from pathlib import Path

import requests
import psycopg2

from ..constants import DEPARTEMENTS
from .. import db
from .. import helpers as hp
from .. import batch as b


def process(departements, forceload, **kwargs):
    departements = set(departements)
    depts_inconnus = departements - set(DEPARTEMENTS)
    if depts_inconnus:
        raise ValueError(f"Départements inconnus : {depts_inconnus}")
    for dept in sorted(departements):
        print(f"Processing {dept}")
        status = download(dept)
        if status or forceload:
            import_to_pg(dept)

def download(departement):
    id_batch = b.batch_start_log("download source", "LD CADASTRE", departement)
    destination = get_destination(departement)
    headers = {}
    if destination.exists():
        headers["If-Modified-Since"] = formatdate(destination.stat().st_mtime)

    resp = requests.get(
        f"https://cadastre.data.gouv.fr/data/etalab-cadastre/latest/geojson/departements/{departement}/cadastre-{departement}-lieux_dits.json.gz",
        headers=headers,
    )
    if resp.status_code == 200:
        with destination.open("wb") as f:
            f.write(resp.content)
        mtime = parsedate_to_datetime(resp.headers["Last-Modified"]).timestamp()
        os.utime(destination, (mtime, mtime))
        b.batch_stop_log(id_batch, True)
        return True
    if resp.status_code == 304:
        b.batch_stop_log(id_batch, True)
        return False

    print(f"Code de téléchargement : {resp.status_code}")
    b.batch_stop_log(id_batch, False)
    return False

def import_to_pg(departement, **kwargs):
    id_batch = b.batch_start_log("import source", "LD CADASTRE", departement)
    fichier_source = get_destination(departement)
    with gzip.open(fichier_source, mode="rt") as f:
        json_source = json.load(f)
        with db.bano_db.cursor() as cur_insert:
            try:
                cur_insert.execute(
                    f"DELETE FROM lieux_dits WHERE code_insee LIKE '{departement+'%'}';COMMIT;"
                )
                a_values = []
                str_query = f"INSERT INTO lieux_dits VALUES "
                for l in json_source["features"]:
                    nom = hp.escape_quotes(l['properties']['nom']).replace("\\","")
                    a_values.append(
                        f"('{l['properties']['commune']}','{nom}','{l['properties']['created']}','{l['properties']['updated']}',ST_SetSRID(ST_GeomFromGeoJSON('{hp.replace_single_quotes_with_double(str(l['geometry']))}'),4326))"
                    )
                if a_values:
                    cur_insert.execute(str_query + ",".join(a_values) + ";COMMIT;")
                b.batch_stop_log(id_batch, True)
            except psycopg2.DataError as e:
                print(e)
                db.bano_db.reset()
                b.batch_stop_log(id_batch, False)

def get_destination(departement):
    try:
        cwd = Path(os.environ["CADASTRE_CACHE_DIR"])
    except KeyError:
        raise ValueError(f"La variable CADASTRE_CACHE_DIR n'est pas définie")
    if not cwd.exists():
        raise ValueError(f"Le répertoire {cwd} n'existe pas")
    return cwd / f"cadastre-{departement}-lieux_dits.json.gz"

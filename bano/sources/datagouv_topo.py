#!/usr/bin/env python

import os
import io
import re
import requests

from pathlib import Path
from email.utils import formatdate, parsedate_to_datetime

from .. import batch as b
from .. import db_helpers as h
from ..constants import DEPARTEMENTS
from ..db import bano_db
from ..sql import sql_process,sql_get_data
from ..import rapprochement as rap

TABLE_CIBLE = 'topo_stage'

def dowload(version):
    id_batch = b.batch_start_log("download source", "TOPO", 'FRA')
    destination = get_destination(version)
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    # https://www.data.gouv.fr/fr/datasets/fichier-des-entites-topographiques-topo-dgfip-1/
    resp = requests.get(f'https://www.data.gouv.fr/fr/datasets/r/906e5bd0-8be8-4150-9956-594fa0e8154c', headers=headers)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        b.batch_stop_log(id_batch, True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def update_table_in_db(version):
    with open(get_destination(version)) as csv:
        csv.readline()
        io_in_csv = io.StringIO()
        dic_res = {}
        for i,line in enumerate(csv):
            if line[16:18] != '14':
                continue
            try:
                code_topo,nature_de_voie,libelle,type_commune_actuel_r_ou_n,type_commune_fip_rounfip,rur_actuel,rur_fip,caractere_voie,annulation,date_annulation,date_cra_c_ation_de_article,type_voie,mot_classant,date_derniere_transition = line.split(';')
            except:
                print('Erreur unpack')
                print(line[0:50])
                continue
            fantoir,code_insee,code_dep = code_topo[7:16],code_topo[7:12],code_topo[7:10] if code_topo[7:9] == '97' else code_topo[7:9]

            if code_dep not in DEPARTEMENTS:
                continue

            date_creation = date_cra_c_ation_de_article.replace('-','')
            date_annulation = int(date_annulation)

            io_in_csv.write(f"{code_dep}${code_insee}${fantoir}${nature_de_voie}${libelle}${caractere_voie}${annulation}${date_annulation}${date_creation}${type_voie}${mot_classant}\n") # separateur $ car on trouve des virgules dans le contenu
        io_in_csv.seek(0)

        with bano_db.cursor() as cur:
            cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_CIBLE} AS SELECT * FROM topo LIMIT 0;")
            cur.execute(f"TRUNCATE {TABLE_CIBLE}")
            cur.copy_from(io_in_csv,f"{TABLE_CIBLE}",sep='$',null='')
    sql_process('topo_comparaison',{})

def get_destination(version):
    return Path(os.environ['DATA_DIR']) / f'{version}.csv'

def publish(diff,full,**kwargs):
    if diff:
        sql_process('topo_publish_incremental',{})
        communes = sql_get_data("topo_communes_ajout_maj",{})
        for c in communes:
            print(f"{c[0]} - {h.nom_commune(c[0])}")
            rap.process(code_insee=c[0],dept=None,verbose=None,source_pifometre=None)
    if full:
        sql_process('topo_publish_full',{})


def process(version, forceload, **kwargs):
    if dowload(version) or forceload:
        update_table_in_db(version)

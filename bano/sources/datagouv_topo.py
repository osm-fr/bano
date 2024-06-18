#!/usr/bin/env python

import os
import io
import re
import requests

from pathlib import Path
from email.utils import formatdate, parsedate_to_datetime

from .. import batch as b
from ..constants import DEPARTEMENTS
from ..db import bano_db

def dowload():
    id_batch = b.batch_start_log("download source", "TOPO", 'FRA')
    destination = get_destination()
    headers = {}
    if destination.exists():
        headers['If-Modified-Since'] = formatdate(destination.stat().st_mtime)

    # https://www.data.gouv.fr/fr/datasets/fichier-des-entites-topographiques-topo-dgfip-1/
    resp = requests.get(f'https://www.data.gouv.fr/fr/datasets/r/49cdb45f-87c4-40d6-92ad-5fcb955f5faa', headers=headers)
    if resp.status_code == 200:
        with destination.open('wb') as f:
            f.write(resp.content)
        b.batch_stop_log(id_batch, True)
        return True
    print(resp.status_code)
    b.batch_stop_log(id_batch, False)
    return False


def update_table_in_db():
    table_cible = 'topo'
    with open(get_destination()) as csv:
        csv.readline()
        io_in_csv = io.StringIO()
        dic_res = {}
        for i,line in enumerate(csv):
            if line[16:18] != '14':
                continue
            code_topo,libelle,type_commune_actuel_r_ou_n,type_commune_fip_rounfip,rur_actuel,rur_fip,caractere_voie,annulation,date_annulation,date_cra_c_ation_de_article,type_voie,mot_classant,date_derniere_transition = line.split(';')
            fantoir,code_insee,code_dep = code_topo[7:16],code_topo[7:12],code_topo[7:10] if code_topo[7:9] == '97' else code_topo[7:9]

            if code_dep not in DEPARTEMENTS:
                continue

            date_creation = date_cra_c_ation_de_article.replace('-','')
            date_annulation = int(date_annulation)

            modified = False
            libelle = re.sub(' +', ' ', libelle)
            if len(libelle) > 4:
                if not modified and libelle[4] == 'D':
                    for m in ['CHEM','COTE','COUR','PONT','PARC','PLAN','PASS','MAIS','MAIL','JARD','PLAG','PIST','CAMI','CALL','ZONE','PTTE','TSSE']:
                        if re.match(f'{m}[D]',libelle):
                            libelle = re.sub(f'^{m}',f'{m} ',libelle)
                            if not m in dic_res:
                                dic_res[m] = 0
                            dic_res[m] = dic_res[m] + 1
                            modified = True
                            break
                if re.match('^CHEM[A-HJ-Z]',libelle):
                    libelle = re.sub('^CHEM','CHEM ',libelle)
                    modified = True
                    if not 'CHEM' in dic_res:
                        dic_res['CHEM'] = 0
                    dic_res['CHEM'] = dic_res['CHEM'] + 1
                for m in ['CITES','CITE','QUAI','VOIES','VOIE','CLOS','VCHE','ZONE','PTTE','TSSE','CTRE']:
                    if re.match(f'{m}[A-Z]',libelle):
                        libelle = re.sub(f'^{m}',f'{m} ',libelle)
                        if not m in dic_res:
                            dic_res[m] = 0
                        dic_res[m] = dic_res[m] + 1
                        modified = True
                        break
                if not modified and re.match('^PROM[A-DF-Z]',libelle):
                    libelle = re.sub('^PROM','PROM ',libelle)
                    modified = True
                    if not 'PROM' in dic_res:
                        dic_res['PROM'] = 0
                    dic_res['PROM'] = dic_res['PROM'] + 1
                if not modified and re.match('^RUIS[A-RT-Z]',libelle):
                    libelle = re.sub('^RUIS','RUIS ',libelle)
                    modified = True
                    if not 'RUIS' in dic_res:
                        dic_res['RUIS'] = 0
                    dic_res['RUIS'] = dic_res['RUIS'] + 1
                if not modified and re.match('^CLOS[A-DF-Z]]',libelle):
                    libelle = re.sub('^CLOS','CLOS ',libelle)
                    modified = True
                    if not 'CLOS' in dic_res:
                        dic_res['CLOS'] = 0
                    dic_res['CLOS'] = dic_res['CLOS'] + 1
                if not modified and re.match('^PORT[DF]',libelle):
                    libelle = re.sub('^PORT','PORT ',libelle)
                    modified = True
                    if not 'PORT' in dic_res:
                        dic_res['PORT'] = 0
                    dic_res['PORT'] = dic_res['PORT'] + 1

            io_in_csv.write(f"{code_dep}${code_insee}${fantoir}$${libelle}${caractere_voie}${annulation}${date_annulation}${date_creation}${type_voie}${mot_classant}\n") # separateur $ car on trouve des virgules dans le contenu
        io_in_csv.seek(0)
        print(dic_res)
        with bano_db.cursor() as cur:
            cur.execute(f"TRUNCATE {table_cible}")
            cur.copy_from(io_in_csv,f"{table_cible}",sep='$',null='')

def get_destination():
    return Path(os.environ['DATA_DIR']) / 'topo.csv'

def process(**kwargs):
    if dowload():
        update_table_in_db()

# stats TOPO decembre 2023
# {'PROM': 1755, 'PASS': 698, 'CHEM': 31929, 'CLOS': 4986, 'VOIE': 2731, 'COUR': 1320, 'COTE': 1007, 'MAIL': 303, 'PTTE': 562, 'PONT': 623, 'PARC': 745, 'CITE': 7793, 'QUAI': 3683, 'PORT': 129, 'RUIS': 716, 'ZONE': 329, 'CITES': 453, 'PIST': 114, 'MAIS': 110, 'VCHE': 227, 'TSSE': 420, 'VOIES': 83, 'CTRE': 590, 'JARD': 49, 'PLAG': 53, 'PLAN': 354, 'CAMI': 1336, 'CALL': 112}

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
from ..sql import sql_process

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
            cur.execute(f"CREATE TABLE IF NOT EXISTS {TABLE_CIBLE} AS SELECT * FROM topo LIMIT 0;")
            cur.execute(f"TRUNCATE {TABLE_CIBLE}")
            cur.copy_from(io_in_csv,f"{TABLE_CIBLE}",sep='$',null='')
    sql_process('topo_comparaison',{})

def get_destination(version):
    return Path(os.environ['DATA_DIR']) / f'{version}.csv'

def publish(**kwargs):
    sql_process('topo_publish',{})

def process(version, forceload, **kwargs):
    # sql_process('topo_comparaison',{})

    if dowload(version) or forceload:
        update_table_in_db(version)

# stats TOPO decembre 2023
# {'PROM': 1755, 'PASS': 698, 'CHEM': 31929, 'CLOS': 4986, 'VOIE': 2731, 'COUR': 1320, 'COTE': 1007, 'MAIL': 303, 'PTTE': 562, 'PONT': 623, 'PARC': 745, 'CITE': 7793, 'QUAI': 3683, 'PORT': 129, 'RUIS': 716, 'ZONE': 329, 'CITES': 453, 'PIST': 114, 'MAIS': 110, 'VCHE': 227, 'TSSE': 420, 'VOIES': 83, 'CTRE': 590, 'JARD': 49, 'PLAG': 53, 'PLAN': 354, 'CAMI': 1336, 'CALL': 112}

# stats TOPO mars 2024
# {'CITE': 7787, 'CTRE': 590, 'VOIE': 2749, 'CHEM': 32485, 'PARC': 746, 'QUAI': 3684, 'COUR': 1324, 'PROM': 1758, 'PONT': 627, 'CLOS': 5006, 'COTE': 1013, 'PASS': 701, 'RUIS': 716, 'PLAG': 53, 'MAIL': 305, 'ZONE': 329, 'VCHE': 227, 'CITES': 453, 'VOIES': 83, 'PTTE': 561, 'PORT': 129, 'MAIS': 110, 'JARD': 52, 'CAMI': 1337, 'PIST': 115, 'TSSE': 420, 'CALL': 113, 'PLAN': 353}

# stats TOPO juillet 2024 (dispo septembre 2024)
# {'CITE': 7788, 'VOIE': 2804, 'CHEM': 31914, 'COUR': 1374, 'MAIL': 308, 'QUAI': 3703, 'PONT': 629, 'PARC': 754, 'CITES': 453, 'CTRE': 590, 'CLOS': 5064, 'COTE': 1046, 'PROM': 1791, 'TSSE': 416, 'ZONE': 337, 'PTTE': 572, 'PASS': 710, 'VCHE': 227, 'VOIES': 83, 'PORT': 130, 'PIST': 117, 'RUIS': 716, 'MAIS': 110, 'CALL': 118, 'JARD': 52, 'PLAG': 53, 'CAMI': 1353, 'PLAN': 358}

# stats TOPO octobre 2024 (dispo octobre 2024)
# {'CHEM': 26317, 'CITE': 7797, 'QUAI': 3705, 'VOIE': 2821, 'COUR': 1488, 'PARC': 760, 'CTRE': 590, 'CLOS': 5084, 'VOIES': 86, 'MAIL': 308, 'CITES': 454, 'PROM': 1801, 'COTE': 1057, 'PTTE': 578, 'PONT': 631, 'ZONE': 337, 'RUIS': 716, 'TSSE': 416, 'PORT': 130, 'VCHE': 228, 'PASS': 564, 'MAIS': 110, 'JARD': 53, 'PLAG': 60, 'CAMI': 1373, 'CALL': 128, 'PLAN': 358, 'PIST': 125}

# stats TOPO décembre 2024
# {'CLOS': 5091, 'RUIS': 716, 'PROM': 1803, 'CITE': 7801, 'CHEM': 14290, 'VOIE': 2822, 'ZONE': 337, 'COTE': 1061, 'QUAI': 3706, 'PASS': 374, 'COUR': 1614, 'CITES': 454, 'MAIL': 309, 'PARC': 761, 'PTTE': 578, 'CTRE': 590, 'PONT': 632, 'PORT': 130, 'TSSE': 416, 'JARD': 53, 'MAIS': 110, 'VCHE': 227, 'VOIES': 86, 'PLAN': 358, 'CAMI': 1374, 'CALL': 129, 'PIST': 127, 'PLAG': 60}

# stats TOPO janvier 2025
# {'CITE': 7794, 'CHEM': 14280, 'VOIE': 2822, 'COUR': 1614, 'PARC': 760, 'QUAI': 3701, 'PONT': 632, 'PORT': 129, 'PROM': 1809, 'VCHE': 226, 'CTRE': 589, 'COTE': 1071, 'MAIL': 310, 'CLOS': 5088, 'CITES': 454, 'PASS': 379, 'PTTE': 580, 'TSSE': 416, 'JARD': 53, 'MAIS': 110, 'ZONE': 336, 'VOIES': 86, 'RUIS': 716, 'PIST': 126, 'CAMI': 1377, 'PLAN': 359, 'CALL': 131, 'PLAG': 60}

# stats TOPO février 2025
# {'VOIE': 2826, 'COUR': 1614, 'CITE': 7801, 'PASS': 379, 'CHEM': 14303, 'CALL': 131, 'PONT': 632, 'CLOS': 5089, 'QUAI': 3701, 'MAIL': 310, 'VCHE': 226, 'ZONE': 336, 'CTRE': 589, 'PROM': 1809, 'PARC': 760, 'VOIES': 86, 'CITES': 454, 'PTTE': 580, 'PORT': 129, 'COTE': 1072, 'TSSE': 416, 'RUIS': 716, 'JARD': 53, 'CAMI': 1377, 'PIST': 126, 'PLAN': 359, 'PLAG': 60, 'MAIS': 110}

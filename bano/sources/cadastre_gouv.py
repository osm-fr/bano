#!/usr/bin/env python

import os
from pathlib import Path
import time

from bs4 import BeautifulSoup
import requests

from ..constants import DEPARTEMENTS, DEPARTEMENTS_3CHAR
from .. import db


def read_from_cadastre_gouv_to_file():
    with requests.Session() as s:
        reponse = s.get('https://www.cadastre.gouv.fr/scpc/rechercherPlan.do')
        token = reponse.text.split('CSRF_TOKEN=')[1].split('"')[0]

    with open(Path(os.environ['DATA_DIR']) / 'code_cadastre.csv', 'w') as output:
        for index, dept in enumerate(DEPARTEMENTS_3CHAR):
            time.sleep(1)
            reponse = BeautifulSoup(s.get(f"https://www.cadastre.gouv.fr/scpc/listerCommune.do?CSRF_TOKEN={token}&codeDepartement={dept}&libelle=&keepVolatileSession=&offset=5000").text, "lxml")
            for e in reponse.find_all(attrs={"class": "parcelles"}):
                y = e.find(title="Ajouter au panier")
                if y is None:
                    continue

                split = y.get('onclick').split("'")
                code_commune = split[1]
                format_type = split[3]

                commune_cp = e.strong.string
                nom_commune = commune_cp[:-9]
                cp = commune_cp[-7:-2]
                output.write(f'{DEPARTEMENTS[index]},{dept},{nom_commune},{cp},{code_commune},{format_type}\n')


def update_table_in_db():
    # print((Path(__file__)).parent.parent / 'sql' / 'load_code_cadastre.sql')
    with open((Path(__file__)).parent.parent / 'sql' / 'load_code_cadastre.sql', 'r') as sqlfile:
        cur_update = db.bano.cursor()
        cur_update.execute(sqlfile.read().replace('./code_cadastre.csv', str(Path(os.environ['DATA_DIR']) / 'code_cadastre.csv')))


def process(**kwargs):
    read_from_cadastre_gouv_to_file()
    update_table_in_db()

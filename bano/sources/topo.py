#!/usr/bin/env python
# coding: UTF-8

import gzip
import io

from ..constants import get_const_code_dir,CODE_VOIE_FANTOIR

from ..db import bano_sources
from .. import helpers as h

CODE_DIR = get_const_code_dir()


def fantoir9_vers_fantoir10(fantoir):
    insee = fantoir[0:5]
    code_dir = CODE_DIR.get(insee,0)
    dept = fantoir[0:2] # pour les DOM le distingo se fait avec le code direction
    commune = insee[2:]
    code_voie = '0123456789ABCDEFGHIJKLMNOPQRSTVWXYZ'.index(fantoir[5:6])
    numero = fantoir[6:]
    cle = 'ABCDEFGHJKLMNPRSTUVWXYZ'[(int(dept+code_dir+commune)*19+code_voie*11+int(numero))%23]

    return(f"{fantoir}{cle}")

def topo_voie_to_csv(ligne_brute):
    longueurs = [5,2,9,2,4,26,40,1,1,1,1,1,1,8,8,1,8,8]
    champs = []
    # champs = 'region,pays,voie,type_topo,nature,libelle,skip,caractere_voie,annulation,date_annulation,date_creation,type_voie,mot_classant,date_transition'
    # pays,dept, insee,fantoir,nature,voie,caractere voie,annul,date annul,creation,mot classant
    for l in longueurs:
        champs.append((ligne_brute[:l]).strip())
        ligne_brute = ligne_brute[l:]
        # print(ligne_brute)
    # selection
    champs = [champs[2]]+champs[4:6]+champs[11:]
    #insee
    champs.insert(0,champs[0][0:5])
    # code dept
    champs.insert(0,h.get_code_dept_from_insee(champs[0]))
    # fantoir
    champs[2] = fantoir9_vers_fantoir10(champs[2])

    return champs


def import_to_pg(**kwargs):
    fichier_source = '/data/download/TOPO20211101.gz'
    io_in_csv = io.StringIO()
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        for i,line in enumerate(f):
            if line[16:18] != '14':
                continue
            # print(line)
            topo_voie_to_csv(line)
            io_in_csv.write(','.join(topo_voie_to_csv(line)))
            if i > 20:
                break

        with  db.bano_sources.cursor() as cur_insert:
            cur_insert.execute(f"DELETE FROM topo WHERE code_insee LIKE '{departement+'%'}'")
            cur_insert.copy_from(f, "topo", sep=';', null='')
            db.bano_cache.commit()

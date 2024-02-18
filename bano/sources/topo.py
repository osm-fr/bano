#!/usr/bin/env python
# coding: UTF-8

import gzip
import io

from ..constants import get_const_code_dir,CODE_VOIE_FANTOIR,DEPARTEMENTS

from ..db import bano_db
from .. import helpers as h
from .. import batch as b

CODE_DIR = get_const_code_dir()


def fantoir9_vers_fantoir10(fantoir):
    insee = fantoir[0:5]
    code_dir = CODE_DIR.get(insee,'0')
    dept = fantoir[0:2] # pour les DOM le distingo se fait avec le code direction
    if dept == '2A':
        dept = '210'
    if dept == '2B':
        dept = '20'
        code_dir = '1' #2B
    commune = insee[2:]
    code_voie = '0123456789ABCDEFGHIJKLMNOPQRSTVWXYZ'.index(fantoir[5:6])
    numero = fantoir[6:]
    cle = 'ABCDEFGHJKLMNPRSTUVWXYZ'[(int(dept+code_dir+commune)*19+code_voie*11+int(numero))%23]

    # print(f"{fantoir}{cle}")
    return(f"{fantoir}{cle}")

def topo_voie_to_csv(ligne_brute):
    longueurs = [5,2,9,2,4,26,40,1,1,1,1,1,1,8,8,1,8,8]
    champs = []
    # champs = 'region,pays,voie,type_topo,nature,libelle,skip,caractere_voie,annulation,date_annulation,date_creation,type_voie,mot_classant,date_transition'
    # pays,dept, insee,fantoir,nature,voie,caractere voie,annul,date annul,creation,mot classant
    for l in longueurs:
        champs.append((ligne_brute[:l]).strip())
        ligne_brute = ligne_brute[l:]
    # selection
    champs = [champs[2]]+champs[4:6]+champs[11:-1]
    #insee
    champs.insert(0,champs[0][0:5])
    # code dept
    champs.insert(0,h.get_code_dept_from_insee(champs[0]))
    # fantoir
    # champs[2] = fantoir9_vers_fantoir10(champs[2])

    return champs


def import_to_pg():
    fichier_source = '/data/download/TOPO20211101.gz'
    # fichier_source = '/data/download/corse.txt.gz'
    io_in_csv = io.StringIO()
    with gzip.open(fichier_source, mode='rt') as f:
        f.readline()  # skip CSV headers
        for i,line in enumerate(f):
            if line[16:18] != '14':
                continue
            # print(line)
            champs = topo_voie_to_csv(line)
            if champs[0] not in DEPARTEMENTS:
                continue
            io_in_csv.write('$'.join(champs)+'\n') # separateur $ car on trouve des virgules dans le contenu
            # if i > 20:
            #     break
        io_in_csv.seek(0)
        with bano_db.cursor() as cur_insert:
            cur_insert.execute("TRUNCATE topo")
            cur_insert.copy_from(io_in_csv, "topo", sep='$',null='')
            bano_db.commit()

def process_topo(**kwargs):
    id_batch = b.batch_start_log('import source', 'TOPO','France','France')
    try:
        import_to_pg()
        b.batch_stop_log(id_batch,True)
    except:
        b.batch_stop_log(id_batch,False)

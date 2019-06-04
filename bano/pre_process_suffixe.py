#!/usr/bin/env python
# coding: UTF-8

import re
import sys
import time
import os,os.path

from .core import load_cadastre_hsnr
from .outils_de_gestion import batch_start_log
from .outils_de_gestion import batch_end_log

from . import db
from .models import Adresses

def collect_adresses_points(selection, adresses):
    kres = {}
    for k in selection:
        kres[k] = []
        for vv in selection[k]['liste']:
            s = 0
            max = 2
            for a in adresses[vv]['numeros']:
                kres[k].append('SELECT \'{:s}\' hameau,\'{:s}\' code_insee,ST_BUFFER(ST_PointFromText(\'POINT({} {})\',4326),0.0003,2) as g'.format(k.replace("'","''"),adresses.code_insee,adresses[vv]['numeros'][a].node.attribs['lon'],adresses[vv]['numeros'][a].node.attribs['lat']))
                s+=1
                if s == max: break
    return kres

def load_suffixe_2_db(adds, code_insee):
    nb_res = 0
    with db.bano_cache.cursor() as cur:
        str_query = f"DELETE FROM suffixe WHERE insee_com = '{code_insee}';COMMIT;"
        cur.execute(str_query)
        for h in adds:
            # Agde (34003): detection de 'Mer' abusif, pas d'autres suffixes dans la commune
            if code_insee == '34003':
                continue
            print('\t{:s}'.format(h))
            str_query = 'INSERT INTO suffixe SELECT ST_Transform(ST_SetSRID((ST_Dump(gu)).geom,4326),3857),code_insee,hameau FROM (SELECT ST_Union(g) gu,code_insee,hameau FROM({:s})a GROUP BY 2,3)a;COMMIT;'.format(' UNION ALL '.join(adds[h]))
            cur.execute(str_query)
            nb_res+=len(adds[h])
    return nb_res

def name_frequency(adresses):
    freq = {}
    for v in adresses:
        s = v.split()
        if len(s)>4:
            k = ' '.join(s[-2:])
            if k not in freq:
                freq[k] = {'nombre':1,'liste':[v]}
            else:
                freq[k]['nombre'] +=1
                freq[k]['liste'].append(v)
        if len(s)>3:
            k = v.split()[-1]
            if k not in freq:
                freq[k] = {'nombre':1,'liste':[v]}
            else:
                freq[k]['nombre'] +=1
                freq[k]['liste'].append(v)
    return freq

def select_street_names_by_name(freq):
    sel = {}
    mots = {}
    for k in freq:
        ks = k.split()
        if freq[k]['nombre'] > 5 and len(ks) > 1:
            mots[ks[0]] = 1
            mots[ks[1]] = 1
            sel[k] = freq[k]
    for k in freq:
        ks = k.split()
        # un suffixe ne peut pas être un numero seul, cas dans les arrdts parisiens
        if freq[k]['nombre'] > 5 and len(ks) == 1 and not k.isdigit() and not k in mots :
            sel[k] = freq[k]
    return sel

def process(code_insee, **kwargs):
    debut_total = time.time()
    source = 'CADASTRE'
    adresses = Adresses(code_insee)
 
    batch_id = batch_start_log(source,'detectesuffixe',code_insee)

    adresses.load_cadastre_hsnr()
    freq = name_frequency(adresses)
    selection = select_street_names_by_name(freq)
    adds = collect_adresses_points(selection, adresses)
    nb_rec = load_suffixe_2_db(adds, code_insee)

    batch_end_log(nb_rec,batch_id)

#!/usr/bin/env python
# coding: UTF-8

import re
import sys
import time
import os, os.path

from . import batch as b
from .db import bano_db
from . import helpers as hp
from . import db_helpers as dh
from .models import Adresses


def name_frequency(adresses):
    freq = {}
    noms_hors_1ere_passe = set()
    for nom in adresses.noms_de_voies:
        s = nom.split()
        # noms avec suffixe entre () quelle que soit leur longueur
        if "(" in nom and nom[-1] == ")":
            k = f"({nom.split('(')[1]}"
            if k not in freq:
                freq[k] = {"nombre": 1, "liste": set(nom)}
            else:
                freq[k]["nombre"] += 1
                freq[k]["liste"].add(nom)
        elif len(s) > 4:
            k = " ".join(s[-2:])
            if k not in freq:
                freq[k] = {"nombre": 1, "liste": set(nom)}
            else:
                freq[k]["nombre"] += 1
                freq[k]["liste"].add(nom)
        elif len(s) > 3:
            k = nom.split()[-1]
            if k not in freq:
                freq[k] = {"nombre": 1, "liste": set(nom)}
            else:
                freq[k]["nombre"] += 1
                freq[k]["liste"].add(nom)
        else:
            noms_hors_1ere_passe.add(nom)

    # 2eme passe sur les noms courts (surtout des lieux-dits) avec un suffixe
    for nom in noms_hors_1ere_passe:
        s = nom.split()
        if len(s) > 1 and len(s) < 4:
            k = nom.split()[-1]
            if k in freq:
                freq[k]["nombre"] += 1
                freq[k]["liste"].add(nom)

    return freq


def select_street_names_by_name(freq):
    sel = {}
    mots = {}
    for k in freq:
        ks = k.split()
        if freq[k]["nombre"] > 5 and len(ks) > 1:
            mots[ks[0]] = 1
            mots[ks[1]] = 1
            sel[k] = freq[k]
    for k in freq:
        ks = k.split()
        # un suffixe ne peut pas être un numero seul, cas dans les arrdts parisiens
        if freq[k]["nombre"] > 5 and len(ks) == 1 and not k.isdigit() and not k in mots:
            sel[k] = freq[k]
    return sel


def collect_adresses_points(selection, adresses):
    kres = {}
    for k in selection:
        kres[k] = []
        for nom_voie in selection[k]["liste"]:
            s = 0
            max = 2
            for i in adresses.index_voie[nom_voie]:
                add = adresses[i]
                suffixe = k.replace("'", "''")
                kres[k].append(
                    f"SELECT '{suffixe}' AS libelle_suffixe,'{adresses.code_insee}' AS code_insee,ST_BUFFER(ST_PointFromText('POINT({add.x} {add.y})',4326),0.0003,2) as g"
                )
                s += 1
                if s == max:
                    break
    return kres


def load_suffixe_2_db(adds, code_insee, nom_commune):
    with bano_db.cursor() as cur:
        for h in adds:
            # Agde (34003): detection de 'Mer' abusif, pas d'autres suffixes dans la commune
            if code_insee == "34003":
                continue
            print(f"{code_insee} - {nom_commune}......... {h}")
            str_query = f"INSERT INTO suffixe SELECT ST_SetSRID((ST_Dump(gu)).geom,4326),code_insee,libelle_suffixe FROM (SELECT ST_Union(g) gu,code_insee,libelle_suffixe FROM({' UNION ALL '.join(adds[h])})a GROUP BY 2,3)a;"
            cur.execute(str_query)


def process(departements, **kwargs):
    for dept in departements:
        if hp.is_valid_dept(dept):
            print(f"Traitement du dept {dept}")
            with bano_db.cursor() as cur:
                str_query = f"DELETE FROM suffixe WHERE insee_com LIKE '{dept}%';"
                cur.execute(str_query)
            for code_insee, nom_commune in dh.get_insee_name_list_by_dept(dept):
                # for code_insee, nom_commune in [['49244','Mauges']]:
                debut_total = time.time()
                # hp.display_insee_commune(code_insee, nom_commune)
                adresses = Adresses(code_insee)
                batch_id = b.batch_start_log("detecte suffixe", code_insee, nom_commune)
                try:
                    adresses.charge_numeros_ban()
                    freq = name_frequency(adresses)
                    selection = select_street_names_by_name(freq)
                    adds = collect_adresses_points(selection, adresses)
                    load_suffixe_2_db(adds, code_insee, nom_commune)
                    b.batch_stop_log(batch_id, True)
                except (e):
                    print(e)
                    b.batch_stop_log(batch_id, False)

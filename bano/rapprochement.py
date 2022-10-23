#!/usr/bin/env python
# coding: UTF-8

from . import db_helpers as h
from . import batch as b
from .models import Noms, Adresses, Topo


def process_unitaire(source,code_insee):
    id_batch = b.batch_start_log('rapprochement', source, code_insee)
    try:
        topo = Topo(code_insee)
        adresses = Adresses(code_insee,source)
        noms = Noms(code_insee,source)

        if source == 'OSM':
            noms.charge_noms_osm_hors_numeros()
            adresses.charge_numeros_osm()

        if source == 'BAN':
            adresses.charge_numeros_ban(topo)

        adresses.noms_des_adresses(noms)
        noms.add_fantoir(topo)
        adresses.enregistre()
        noms.enregistre()
        b.batch_stop_log(id_batch,True)
    except:
        b.batch_stop_log(id_batch,False)


def process(source,code_insee,dept,**kwargs):
    if dept:
        liste_insee = h.liste_communes_par_dept(dept)
    else:
        liste_insee = [(code_insee,h.nom_commune(code_insee))]
    for code_insee,nom in liste_insee:
        if dept:
            print(f"{code_insee} - {nom}")
        process_unitaire(source,code_insee)

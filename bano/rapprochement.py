#!/usr/bin/env python
# coding: UTF-8

from . import db_helpers as h
from . import batch as b
from .models import Noms, Adresses, Topo, Points_nommes, Correspondance_fantoir_ban_osm
from .sources import ban2topo


def process_unitaire(code_insee):
    id_batch = b.batch_start_log("rapprochement", "toutes", code_insee)
    try:
        ban2topo.process(code_insee)
        topo = Topo(code_insee)
        adresses = Adresses(code_insee)
        points_nommes = Points_nommes(code_insee)
        noms = Noms(code_insee)
        correspondance_fantoir_ban_osm = Correspondance_fantoir_ban_osm(code_insee)

        noms.charge_noms_osm_hors_numeros()
        adresses.charge_numeros_osm()
        adresses.charge_numeros_ban(topo)
        points_nommes.charge_points_nommes_lieux_dits_cadastre()
        points_nommes.charge_points_nommes_centroides_osm()
        points_nommes.charge_points_nommes_place_osm()

        adresses.noms_des_adresses(noms)
        points_nommes.noms_des_points_nommes(noms)

        noms.add_fantoir(topo)
        noms.remplit_fantoir_par_nom_sous_commune()
        points_nommes.complete_fantoir(noms)
        adresses.complete_fantoir(noms)

        correspondance_fantoir_ban_osm.process(noms)

        adresses.enregistre(correspondance_fantoir_ban_osm.correspondance)
        noms.enregistre(correspondance_fantoir_ban_osm.correspondance)
        points_nommes.enregistre(correspondance_fantoir_ban_osm.correspondance)

        b.batch_stop_log(id_batch, True)
    except:
        b.batch_stop_log(id_batch, False)


def process(code_insee, dept, **kwargs):
    if dept:
        liste_insee = h.liste_communes_par_dept(dept)
    else:
        liste_insee = [(code_insee, h.nom_commune(code_insee))]
    for code_insee, nom in liste_insee:
        if dept:
            print(f"{code_insee} - {nom}")
        process_unitaire(code_insee)

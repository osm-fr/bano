#!/usr/bin/env python
# coding: UTF-8

import json

from . import db_helpers as h
from . import batch as b
from .sql import sql_process
from .models import Noms, Adresses, Topo, Points_nommes, Correspondance_fantoir_ban_osm
from .sources import ban2topo


def process_unitaire(code_insee,verbose,source_pifometre):
    if source_pifometre:
        source = 'pifometre'
    else :
        source = 'BANO quotidien'
    id_batch = b.batch_start_log("rapprochement", source, code_insee)
    try:
        if verbose: print('ban2topo')
        ban2topo.process(code_insee)
        if verbose: print('topo')
        topo = Topo(code_insee)
        if verbose: print('adresses')
        adresses = Adresses(code_insee)
        if verbose: print('points_nommes')
        points_nommes = Points_nommes(code_insee)
        if verbose: print('noms')
        noms = Noms(code_insee)
        if verbose: print('correspondance_fantoir_ban_osm')
        correspondance_fantoir_ban_osm = Correspondance_fantoir_ban_osm(code_insee)

        if verbose: print('charge_noms_osm_hors_numeros')
        noms.charge_noms_osm_hors_numeros()
        adresses.charge_numeros_osm()
        adresses.charge_numeros_ban(topo)
        points_nommes.charge_points_nommes_lieux_dits_cadastre()
        points_nommes.charge_points_nommes_place_osm()
        # Les centroïdes viennent en dernier (fallback). Tout point déjà affecté comme lieu-dit OSM est inchangé dans l'étape charge_points_nommes_centroides_osm()
        if verbose: print('charge_points_nommes_centroides_osm')
        points_nommes.charge_points_nommes_centroides_osm()
        if verbose: print('charge_points_nommes_numeros_ban')
        points_nommes.charge_points_nommes_numeros_ban()

        if verbose: print('noms_des_adresses')
        adresses.noms_des_adresses(noms)
        if verbose: print('noms_des_points_nommes 1')
        points_nommes.noms_des_points_nommes(noms)

        if verbose: print('noms.add_fantoir')
        noms.add_fantoir(topo)
        if verbose: print('noms.remplit_fantoir_par_nom_sous_commune')
        noms.remplit_fantoir_par_nom_sous_commune()
        if verbose: print('points_nommes.complete_fantoir')
        points_nommes.complete_fantoir(noms)

        # 2e passe suite au complément Fantoir
        if verbose: print('points_nommes.noms_des_points_nommes 2')
        points_nommes.noms_des_points_nommes(noms)
        if verbose: print('adresses.complete_fantoir')
        adresses.complete_fantoir(noms)

        if verbose: print('correspondance_fantoir_ban_osm')
        correspondance_fantoir_ban_osm.process(noms)

        if verbose: print('adresses.enregistre')
        adresses.enregistre(correspondance_fantoir_ban_osm.correspondance)
        if verbose: print('noms.enregistre')
        noms.enregistre(correspondance_fantoir_ban_osm.correspondance)
        if verbose: print('points_nommes.enregistre')
        points_nommes.enregistre(correspondance_fantoir_ban_osm.correspondance)

        nb_addr_ban, nb_addr_osm, nb_noms_addr_osm = adresses.stats_sources(noms)
        nb_noms_ban, nb_noms_cadastre, nb_noms_osm = noms.stats_sources()
        nb_noms_topo = topo.nb_fantoirs
        sql_process(
            "update_table_bano_stats_communales",
            dict(
                code_insee=code_insee,
                nb_adresses_osm=str(nb_addr_osm),
                nb_adresses_ban=str(nb_addr_ban),
                nb_noms_adr_osm=str(nb_noms_adr_osm),
                nb_noms_osm=str(nb_noms_osm),
                nb_noms_ban=str(nb_noms_ban),
                nb_noms_topo=str(nb_noms_topo),
                nb_noms_cadastre=str(nb_noms_cadastre),
            ),
        )

        b.batch_stop_log(id_batch, True)
    except Exception as e:
        if verbose:
            print(e)
        b.batch_stop_log(id_batch, False)


def process(code_insee, dept, verbose, source_pifometre, **kwargs):
    if dept:
        liste_insee = h.liste_communes_par_dept(dept)
    else:
        liste_insee = [(code_insee, h.nom_commune(code_insee))]
    for code_insee, nom in liste_insee:
        if dept or verbose:
            print(f"{code_insee} - {nom}")
        process_unitaire(code_insee,verbose,source_pifometre)

#!/usr/bin/env python
# coding: UTF-8

import json
from time import time,sleep
from random import random
import os
from pathlib import Path

from . import db_helpers as h
from . import batch as b
from .sql import sql_process
from .models import Noms, Adresses, Topo, Points_nommes, Correspondance_fantoir_ban_osm
from .sources import pseudotopo


def process_unitaire(code_insee,verbose,source_pifometre):
    if source_pifometre and not set_lock(code_insee):
        return False

    if source_pifometre:
        source = 'pifometre'
    else :
        source = 'BANO quotidien'
    id_batch = b.batch_start_log("rapprochement", source, code_insee)
    try:
        if verbose: print('pseudotopo')
        pseudotopo.process(code_insee)
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
        if verbose: print('charge_numeros_osm')
        adresses.charge_numeros_osm()
        if verbose: print('charge_numeros_ban')
        adresses.charge_numeros_ban(topo)
        if verbose: print('charge_points_nommes_lieux_dits_cadastre')
        points_nommes.charge_points_nommes_lieux_dits_cadastre()
        if verbose: print('charge_points_nommes_place_osm')
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
        noms.remplit_fantoir_osm_par_fantoir_ban()
        if verbose: print('points_nommes.complete_fantoir')
        points_nommes.complete_fantoir(noms)

        # 2e passe suite au complément Fantoir
        if verbose: print('points_nommes.noms_des_points_nommes 2')
        points_nommes.noms_des_points_nommes(noms)
        if verbose: print('adresses.complete_fantoir')
        adresses.complete_fantoir(noms)

        # rattachement des noms alt_, old_ et en langues régionales en privilégiant le FANTOIR du tag name
        noms.lien_fantoir_entre_noms(points_nommes)

        if verbose: print('correspondance_fantoir_ban_osm')
        correspondance_fantoir_ban_osm.process(noms)

        if verbose: print('adresses.enregistre')
        adresses.enregistre(correspondance_fantoir_ban_osm.correspondance)
        if verbose: print('noms.enregistre')
        noms.enregistre(correspondance_fantoir_ban_osm.correspondance)
        if verbose: print('points_nommes.enregistre')
        points_nommes.enregistre(correspondance_fantoir_ban_osm.correspondance)

        nb_addr_ban, nb_addr_osm, nb_noms_adr_osm = adresses.stats_sources(noms,correspondance_fantoir_ban_osm.correspondance)
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
    if source_pifometre:
        release_lock(code_insee)

def get_lockfile(lock_name):
    try:
        lock_dir = Path(os.environ["LOCK_DIR"])
    except KeyError:
        raise ValueError(f"La variable LOCK_DIR n'est pas définie")
    if not lock_dir.exists():
        raise ValueError(f"Le répertoire {lock_dir} n'existe pas")
    return lock_dir / f"{lock_name}.lock"

def is_active_lock(lock_name):
    lock_file = get_lockfile(lock_name)

    if lock_file.exists() and (time() - lock_file.stat().st_mtime) < 300:
        return True
    return False

def set_lock(lock_name):
    lock_file = get_lockfile(lock_name)
    try :
        lock_file.touch(exist_ok=False)
        return True
    except:
        return False

def release_lock(lock_name):
    lock_file = get_lockfile(lock_name)
    lock_file.unlink(missing_ok=True)

def process(code_insee, dept, verbose, source_pifometre, **kwargs):
    if dept:
        liste_insee = h.liste_communes_par_dept(dept)
    else:
        liste_insee = [(code_insee, h.nom_commune(code_insee))]
    for code_insee, nom in liste_insee:
        if dept or verbose:
            print(f"{code_insee} - {nom}")
        # temporisation aléatoire pour ventiler les possibles appels concurrents provenants d'un même clic
        if source_pifometre:
            sleep(3 * random())
        if  not (source_pifometre and is_active_lock(code_insee)):
            process_unitaire(code_insee,verbose,source_pifometre)

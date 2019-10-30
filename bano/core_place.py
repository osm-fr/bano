#!/usr/bin/env python
# coding: UTF-8

# Place : ID = Fantoir quand présent, sinon nom normalisé
# 1- chargement Fantoir
# 2- chargement cadastre, rapprochement Fantoir, géométrie Cadastre calculée des parcelles
# 3- chargement OSM, rapprochement Fantoir, géométrie OSM
# 4- 

import sys
import time
import os

from . import constants, db
from . import helpers as hp
from . import db_helpers as dbhp
from .sources import fantoir
from .models import Fantoir, Cadastre, Osm, Place, Places

from .outils_de_gestion import batch_start_log, batch_end_log

def get_data_from_pg(query_name,insee_com):
    with db.bano_cache.cursor() as conn:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(query_name)),'r') as fq:
            conn.execute(fq.read().replace('__com__',insee_com))
            res = []
            for l in conn :
                res.append(list(l))
    return res


def load_cadastre(code_insee):
    data = get_data_from_pg('cadastre_2_place',code_insee)
    for lon, lat, name, fantoir, *others in data:
        targets = places.match_name(name,'FANTOIR')
        if targets:
            for t in targets:
                places.p[t].update_cadastre(lon,lat,name)
        else:
            places.add_place(Place(lon,lat,'','',name,'',fantoir,-1,code_insee))


def load_fantoir(liste_fantoir):
    for c in liste_fantoir:
        places.add_place(Place(0,0,'',fantoir.mapping.fantoir[c]['nom'],'','',c,fantoir.mapping.fantoir[c]['ld_bati'], c[0:5]))


def load_osm(code_insee):
    data = get_data_from_pg('place_insee',code_insee)
    for lon, lat, place, name, fantoir, ld_bati, tags, *others in data:
        targets = places.match_name(name,'FANTOIR')
        if targets:
            for t in targets:
                places.p[t].update_osm(lon, lat, place, name, fantoir)
        else:
            places.add_place(Place(lon, lat, place,'','',name,fantoir,-1, code_insee))


def load_to_db(places, code_insee):
    with db.bano.cursor() as conn:
        conn.execute(f"DELETE FROM cumul_places WHERE insee_com = '{code_insee}'")

        sload = "INSERT INTO cumul_places (geometrie,libelle_cadastre,libelle_osm,libelle_fantoir,fantoir,insee_com,dept,code_postal,source,ld_bati,ld_osm) VALUES"
        a_values = places.as_SQL_Cadastre_array()
        nb_rec = len(a_values)
        if nb_rec>0:
            conn.execute(sload+','.join(a_values))
        a_values = places.as_SQL_OSM_array()
        if len(a_values)>0:
            conn.execute(sload+','.join(a_values))
        nb_rec+=len(a_values)
    return(nb_rec)

def place_2_db(code_insee):
    global fantoir,places
    format_cadastre = dbhp.get_cadastre_format(code_insee)
    places = Places()

    fantoir.mapping.reset()
    fantoir.mapping.load_lieux_dits(code_insee)
    load_fantoir(fantoir.mapping.fantoir)

    batch_id_osm = batch_start_log('OSM','cumulPlaces',code_insee)

    if format_cadastre == 'VECT':
        batch_id_cadastre = batch_start_log('CADASTRE','cumulPlaces',code_insee)
        load_cadastre(code_insee)
    load_osm(code_insee)
        
    nb_rec = load_to_db(places, code_insee)
    batch_end_log(nb_rec,batch_id_osm)
    if format_cadastre == 'VECT':
        batch_end_log(nb_rec,batch_id_cadastre)

def process(code_insee, depts, France, **kwargs):
    liste_codes_insee = []
    if code_insee:
        liste_codes_insee = dbhp.get_insee_name(code_insee)
    if not liste_codes_insee:
        for d in (depts or France):
            liste_codes_insee += dbhp.get_insee_name_list_by_dept(d)
    for code_insee, nom in liste_codes_insee:
        print(f"{code_insee} - {nom}")
        place_2_db(code_insee)


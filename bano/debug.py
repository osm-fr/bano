#!/usr/bin/env python
# coding: UTF-8

import os,os.path
import re
import sys
import time
import xml.etree.ElementTree as ET

from . import constants, db
from . import helpers as hp
from . import db_helpers as dbhp
from . import log_2_file as log 
from .models import Adresse, Adresses, Node, Pg_hsnr
from .outils_de_gestion import batch_start_log
from .outils_de_gestion import batch_end_log
# from .outils_de_gestion import age_etape_dept
from .sources import fantoir,ban2fantoir

def get_data_from_pg_direct(query_name,insee_com):
    res = []
    with db.bano_cache.cursor() as cur_cache:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}_nocache.sql'.format(query_name)),'r') as fq:
            str_query = fq.read().replace('__com__',insee_com)
            cur_cache.execute(str_query)
    
            for l in cur_cache :
                res.append(list(l))
    return res

def print_data(data,requete):
    for d in data:
        print(f"{requete} - {d}")

def show_ban_hsnr(code_insee):
    data = get_data_from_pg_direct('ban_hsnr',code_insee)
    print_data(data,'ban_hsnr')

def show_hsnr_bbox_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('hsnr_bbox_insee',insee_com)
    print_data(data,'hsnr_bbox')

def show_hsnr_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('hsnr_insee', insee_com)
    print_data(data,'hsnr')

def show_highways_bbox_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('highway_suffixe_insee',insee_com)
    print_data(data,'highways_bbox')

def show_highways_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('highway_suffixe_insee',insee_com)
    print_data(data,'highways')

def show_highways_relations_bbox_from_pg_osm(code_insee):
    data = get_data_from_pg_direct('highway_relation_suffixe_insee_bbox', code_insee)
    print_data(data,'highways_relations_bbox')

def show_highways_relations_from_pg_osm(code_insee):
    data = get_data_from_pg_direct('highway_relation_suffixe_insee', code_insee)
    print_data(data,'highways_relations')

def show_point_par_rue_from_pg_osm(code_insee):
    data = get_data_from_pg_direct('point_par_rue_insee',code_insee)
    print_data(data,'point_par_rue')

def show_point_par_rue_complement_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('point_par_rue_complement_insee',insee_com)
    print_data(data,'point_par_rue_complement')


def print_sql(code_insee, source):
    if source == 'BAN':
        show_ban_hsnr(code_insee)
    if source == 'OSM':
        show_hsnr_from_pg_osm(code_insee)
        show_hsnr_bbox_from_pg_osm(code_insee)

    show_highways_from_pg_osm(code_insee)
    show_highways_relations_from_pg_osm(code_insee)
    show_highways_bbox_from_pg_osm(code_insee)
    show_highways_relations_bbox_from_pg_osm(code_insee)
    show_point_par_rue_from_pg_osm(code_insee)
    show_point_par_rue_complement_from_pg_osm(code_insee)

def process_sql(source, code_insee, **kwargs):
    liste_codes_insee = []
    # code_insee, nom = dbhp.get_insee_name(code_insee)
    print_sql(code_insee, source)


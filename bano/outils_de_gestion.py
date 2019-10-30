#!/usr/bin/env python
# coding: UTF-8

import time
from . import db

def batch_start_log(source,etape,code_geo):
    t = time.localtime()
    th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
    t = round(time.mktime(t),0)
    if len(str(code_geo)) > 3:
        code_insee = code_geo
        dept = None
    else:
        code_insee = None
        dept = code_geo

    with db.bano.cursor() as cur:
        if code_insee:
            whereclause = f"insee_com = '{code_insee}' AND source = '{source}' AND etape = '{etape}'"
            str_query = f"INSERT INTO batch_historique (SELECT * FROM batch WHERE {whereclause});DELETE FROM batch WHERE {whereclause};INSERT INTO batch (source,etape,timestamp_debut,date_debut,dept,insee_com,nom_com,nombre_adresses) SELECT '{source}','{etape}',{t},'{th}',dept,insee_com,nom_com,0 FROM code_cadastre WHERE insee_com = '{code_insee}';COMMIT;"
        if dept:
            whereclause = f"dept = '{dept}' AND source = '{source}' AND etape = '{etape}'"
            str_query = f"INSERT INTO batch_historique (SELECT * FROM batch WHERE {whereclause});DELETE FROM batch WHERE {whereclause};INSERT INTO batch (source,etape,timestamp_debut,date_debut,dept,nombre_adresses) VALUES ('{source}','{etape}',{t},'{th}','{dept}',0);COMMIT;"
        
        # print(str_query)
        cur.execute(str_query)
        print(str_query)

        cur.execute(f"SELECT id_batch::integer FROM batch WHERE {whereclause};")
        c = cur.fetchone()
        return c[0]

def batch_end_log(nb,batch_id):
    with db.bano.cursor() as cur:
        t = time.localtime()
        th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
        whereclause = 'id_batch = {:d}'.format(batch_id)
        cur.execute(f"UPDATE batch SET nombre_adresses = {nb},date_fin = '{th}' WHERE {whereclause};")

def get_cadastre_etape_timestamp_debut(code_cadastre,etape,source):
    str_query = "SELECT timestamp_debut FROM batch WHERE cadastre_com = '{:s}' AND etape = '{:s}' AND source = '{:s}';".format(code_cadastre,etape,source)
    cur = db.bano.cursor()
    cur.execute(str_query)
    for c in cur:
        code_cadastre = c[0]
    return code_cadastre

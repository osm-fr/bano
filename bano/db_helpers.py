import time

from . import db


def get_insee_name_list_by_dept(dept):
    with db.bano.cursor() as conn :
        conn.execute(f"SELECT insee_com, nom_com FROM code_cadastre WHERE dept = '{dept}' ORDER BY 1;")
        return conn.fetchall()

def get_insee_name(insee_com):
    with db.bano.cursor() as conn :
        conn.execute(f"SELECT insee_com, nom_com FROM code_cadastre WHERE insee_com = '{insee_com}';")
        return conn.fetchall()

def age_etape_dept(etape,dept):
    cur = db.bano.cursor()
    str_query = 'SELECT timestamp_debut FROM batch WHERE etape = \'{:s}\' AND dept = \'{:s}\' UNION ALL SELECT 0 ORDER BY 1 DESC;'.format(etape,dept)
    cur.execute(str_query)
    c = cur.fetchone()
    return round(time.mktime(time.localtime()),0) - c[0]

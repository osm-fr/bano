import time
import os

from . import db


def get_insee_name_list_by_dept(dept):
    with db.bano.cursor() as conn :
        conn.execute(f"""SELECT com, ncc
                         FROM cog_commune c
                         LEFT OUTER JOIN (SELECT comparent FROM cog_commune WHERE dep = '{dept}' AND typecom = 'ARM') p
                         ON (c.com = p.comparent)
                         WHERE c.dep = '{dept}' AND c.typecom != 'COMD' AND p.comparent IS NULL
                         ORDER BY 1""")
        return conn.fetchall()

def get_insee_name(insee_com):
    with db.bano.cursor() as conn :
        conn.execute(f"SELECT insee_com, nom_com FROM code_cadastre WHERE insee_com = '{insee_com}';")
        return conn.fetchall()

def get_cadastre_format(insee_com):
    with db.bano.cursor() as conn :
        conn.execute(f"SELECT format_cadastre FROM code_cadastre WHERE insee_com = '{insee_com}';")
        return conn.fetchone()[0]

def age_etape_dept(etape,dept):
    cur = db.bano.cursor()
    str_query = 'SELECT timestamp_debut FROM batch WHERE etape = \'{:s}\' AND dept = \'{:s}\' UNION ALL SELECT 0 ORDER BY 1 DESC;'.format(etape,dept)
    cur.execute(str_query)
    c = cur.fetchone()
    return round(time.mktime(time.localtime()),0) - c[0]

def process_sql(database,query_name,dict_args):
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(query_name)),'r') as fq:
        str_query = fq.read()
        for k,v in dict_args.items():
            str_query = str_query.replace(k,str(v))
    with database.cursor() as cur :
        cur.execute(str_query)

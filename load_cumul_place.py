#!/usr/bin/env python
# -*- coding: utf-8 -*-

import place_2_db as a
import log_2_file as e
import outils_de_gestion as o
import sys
import os,os.path

# Wrap sys.stdout with a writer that knows how to handle encoding
# Unicode data.
# wrapped_stdout = codecs.getwriter('UTF-8')(sys.stdout)
# Replace sys.stdout with a writer
# sys.stdout = wrapped_stdout

def get_sql_like_dept_string(dept):
    return (dept+'___')[0:5]

def get_code_dept_from_insee(insee):
    code_dept = insee[0:2]
    if insee[0:2] == '97':
        code_dept = insee[0:3]
    return code_dept
def get_data_by_dept_from_pg(query_name,dept):
    if dept[0:1] == '0':
        dept = dept[1:]
    etape_dept = 'cache_dept_'+query_name
# Cache gardé 1h
    if o.age_etape_dept(etape_dept,dept) > 1 : #3600:
        print(u'Mise à jour du cache "{:s}"'.format(query_name.upper()))
        batch_id = o.batch_start_log('',etape_dept,dept)
        fq = open('sql/{:s}.sql'.format(query_name),'r')
        str_query = fq.read().replace(" = '__com__'"," LIKE  '{:s}'".format(get_sql_like_dept_string(dept)))
        fq.close()
        pgc = a.get_pgc_osm()
        cur = pgc.cursor()
        cur.execute(str_query)
        o.batch_end_log(0,batch_id)

str_usage = 'USAGE : python load_cumul_place.py <numero de dept|FRANCE>'
if len(sys.argv) != 2:
    print('Mauvais nombre d\'arguments')
    print(str_usage)
    os._exit(0)

if sys.argv[1].upper() == 'FRANCE':
    loop_query = 'SELECT DISTINCT dept FROM code_cadastre ORDER BY 1;'
else:
    num_dept_cadastre = sys.argv[1]
    loop_query = "SELECT '{:s}';".format(num_dept_cadastre)

pgc = a.get_pgc()
cur_loop = pgc.cursor()
cur_loop.execute(loop_query)
for c_loop in cur_loop:
    num_dept_cadastre = c_loop[0]
    global f_log
    f_log = e.start_log_to_file('',os.path.basename(sys.argv[0]).split('.')[0],num_dept_cadastre)
    print('## Département {:s}'.format(num_dept_cadastre))

    get_data_by_dept_from_pg('place_insee',num_dept_cadastre)
    get_data_by_dept_from_pg('cadastre_2_place',num_dept_cadastre)
    
    str_query = "SELECT insee_com,nom_com FROM code_cadastre WHERE dept = '{:s}' ORDER BY 2;".format(num_dept_cadastre)
    cur = pgc.cursor()
    cur.execute(str_query)
    for c in cur:
        print('{:s} - {:s}'.format(c[0],c[1]))
        try:
            a.main(['',c[0],True])
        except :
            e.write_log_to_file(f_log,"Commune : {:s}\n".format(c[1]))
            e.write_log_to_file(f_log,str(sys.exc_info()[0]))
            e.write_log_to_file(f_log,str(sys.exc_info()[1]))
            e.write_sep_to_file(f_log)
    e.end_log_to_file(f_log,True)


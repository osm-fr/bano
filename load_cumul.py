#!/usr/bin/env python
# -*- coding: utf-8 -*-

import addr_2_db as a
import log_2_file as e
import outils_de_gestion as o
import sys
import time
import os,os.path
import codecs

os.umask(0000)

# Wrap sys.stdout with a writer that knows how to handle encoding
# Unicode data.
# wrapped_stdout = codecs.getwriter('UTF-8')(sys.stdout)
# Replace sys.stdout with a writer
# sys.stdout = wrapped_stdout


def get_code_dept_from_insee(insee):
    code_dept = insee[0:2]
    if insee[0:2] == '97':
        code_dept = insee[0:3]
    return code_dept
def get_sql_like_dept_string(dept):
    return (dept+'___')[0:5]
def get_geom_suffixes(dept):
    fq = open('sql/geom_suffixes_insee.sql','r')
    str_query = fq.read().replace("='__com__"," LIKE  '{:s}'".format(get_sql_like_dept_string(dept)))
    print(str_query)
    cursor_bano_ro = pgc.cursor()
    cursor_bano_ro.execute(str_query)
    a_queries = []
    for l in cursor_bano_ro :
        a_queries.append("SELECT ST_PolygonFromText('{:s}',3857) as geom,'{:s}'::text suffixe".format(l[0],l[1].replace('\'','\'\'')))
    cursor_bano_ro.close()
    print(" UNION '.join(a_queries)")
    print(' UNION '.join(a_queries))
    return ' UNION '.join(a_queries)
def warning_message_no_suffixe(dept,etape):
    print("Pas de commune à suffixe dans le {}. Etape {} ignorée".format(dept,etape.upper()))

def get_data_by_dept_from_pg(query_name,dept,suffixe_data=None):
    current_time = round(time.time())
    etape_dept = 'cache_dept_'+query_name
# Cache gardé 1h
    if o.age_etape_dept(etape_dept,dept) > 3600 :
        print(u'Mise à jour du cache "{:s}"'.format(query_name.upper()))
        batch_id = o.batch_start_log(source,etape_dept,dept)
        fq = open('sql/{:s}.sql'.format(query_name),'r')
        str_query = fq.read().replace('=\'__com__',' LIKE  \'{:s}'.format(get_sql_like_dept_string(dept)))
        if suffixe_data :
            str_query = str_query.replace('__suffixe_data__',suffixe_data)
            print(str_query)            
        fq.close()
        cur_osm_ro = pgcl.cursor()
        cur_osm_ro.execute(str_query)

        list_output = list()
        for lt in cur_osm_ro :
            list_values = list()
            for item in list(lt):
                if item == None:
                    list_values.append('null')
                elif  type(item) == str :
                    list_values.append("'{}'".format(item.replace("'","''").replace('"','')))
                elif type(item) == list :
                    if (len(item)) > 0 :
                        list_values.append("hstore(ARRAY{})".format(str([s.replace("'","''").replace('"','') for s in item])))
                    else :
                        list_values.append('null')
                else :
                    list_values.append(str(item))
            list_values.append(str(current_time))

            str_values = ','.join(list_values).replace('"',"'")
            list_output.append(str_values)
        cur_osm_ro.close()
        cur_bano_rw = pgc.cursor()
        str_query = "DELETE FROM {} WHERE insee_com LIKE '{}';".format(query_name,get_sql_like_dept_string(dept))
        cur_bano_rw.execute(str_query)
        if len(list_output) > 0 :
            str_query = "INSERT INTO {} VALUES ({});COMMIT;".format(query_name,'),('.join(list_output))
            cur_bano_rw.execute(str_query)

        o.batch_end_log(0,batch_id)

str_usage = 'USAGE : python load_cumul.py <numero de dept|FRANCE> <OSM|CADASTRE>'
if len(sys.argv) != 3:
    print('Mauvais nombre d\'arguments')
    print(str_usage)
    os._exit(0)
source = sys.argv[2].upper()
if source != 'OSM' and source != 'CADASTRE':
    print('La source doit etre OSM ou CADASTRE')
    print(str_usage)
    os._exit(0)

clause_vecteur = ''
if source == 'CADASTRE':
    clause_vecteur = ' AND format_cadastre = \'VECT\' '

pgc = a.get_pgc()
pgcl = a.get_pgc_layers()

if sys.argv[1].upper() == 'FRANCE':
    loop_query = 'SELECT DISTINCT dept FROM code_cadastre ORDER BY 1;'
else:
    num_dept_cadastre = sys.argv[1]
    loop_query = "SELECT '{:s}';".format(num_dept_cadastre)

cur_loop = pgc.cursor()
cur_loop.execute(loop_query)
for c_loop in cur_loop:
    num_dept_cadastre = c_loop[0]
    global f_log
    f_log = e.start_log_to_file(source,os.path.basename(sys.argv[0]).split('.')[0],num_dept_cadastre)
    print('## Département {:s}'.format(num_dept_cadastre))
    geom_suffixe = get_geom_suffixes(num_dept_cadastre)
    print(geom_suffixe)
    if source == 'OSM':
        get_data_by_dept_from_pg('hsnr_insee',num_dept_cadastre)
        if geom_suffixe :
            get_data_by_dept_from_pg('hsnr_suffixe_insee',num_dept_cadastre,geom_suffixe)
        else :
            warning_message_no_suffixe(num_dept_cadastre,'hsnr_suffixe_insee')
        get_data_by_dept_from_pg('hsnr_bbox_insee',num_dept_cadastre)
        get_data_by_dept_from_pg('point_par_rue_insee',num_dept_cadastre)
        get_data_by_dept_from_pg('point_par_rue_complement_insee',num_dept_cadastre)
        get_data_by_dept_from_pg('type_highway_insee',num_dept_cadastre)
    # os._exit(0)
    
    get_data_by_dept_from_pg('highway_insee',num_dept_cadastre)
    if geom_suffixe :
        get_data_by_dept_from_pg('highway_suffixe_insee',num_dept_cadastre,geom_suffixe)
    else :
        warning_message_no_suffixe(num_dept_cadastre,'highway_suffixe_insee')
    get_data_by_dept_from_pg('highway_bbox_insee',num_dept_cadastre)
    get_data_by_dept_from_pg('highway_relation_insee',num_dept_cadastre)
    if geom_suffixe :
        get_data_by_dept_from_pg('highway_relation_suffixe_insee',num_dept_cadastre,geom_suffixe)
    else :
        warning_message_no_suffixe(num_dept_cadastre,'highway_relation_suffixe_insee')
    get_data_by_dept_from_pg('highway_relation_bbox_insee',num_dept_cadastre)
    # os._exit(0)

    clause_vecteur = ''
    if source == 'CADASTRE':
        clause_vecteur = ' AND format_cadastre = \'VECT\' '
    str_query = 'SELECT insee_com,nom_com FROM code_cadastre WHERE cadastre_dept = \'{:s}\' {:s} ORDER BY 2;'.format(num_dept_cadastre,clause_vecteur)
    cur = pgc.cursor()
    cur.execute(str_query)
    for c in cur:
        print('{:s} - {:s}'.format(c[0],c[1]))
        try:
            a.main(['',c[0],source])
        except :
            e.write_log_to_file(f_log,'Commune : {:s}\n'.format(c[1]))
            e.write_log_to_file(f_log,str(sys.exc_info()[0]))
            e.write_log_to_file(f_log,str(sys.exc_info()[1]))
            e.write_sep_to_file(f_log)
    e.end_log_to_file(f_log,True)


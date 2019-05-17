#!/usr/bin/env python
# coding: UTF-8

import time
from . import db

def batch_start_log(source,etape,code_insee):
	t = time.localtime()
	th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
	t = round(time.mktime(t),0)
	cur = db.bano.cursor()
	if len(etape)>10 and etape[0:10] == 'cache_dept':
		whereclause = "dept = '{:s}' AND etape = '{:s}'".format(code_insee,etape)
	else:
		whereclause = "insee_com = '{:s}' AND source = '{:s}' AND etape = '{:s}'".format(code_insee,source,etape)
	str_query = 'INSERT INTO batch_historique (SELECT * FROM batch WHERE {:s});'.format(whereclause)
	str_query = str_query+'DELETE FROM batch WHERE {:s};'.format(whereclause)
	if len(etape)>10 and etape[0:10] == 'cache_dept':
		str_query = str_query+"INSERT INTO batch (etape,timestamp_debut,date_debut,dept,nombre_adresses) SELECT '{:s}',{:f},'{:s}','{:s}',0;".format(etape,t,th,code_insee)
	else:
		str_query = str_query+"INSERT INTO batch (source,etape,timestamp_debut,date_debut,dept,insee_com,nom_com,nombre_adresses) SELECT '{:s}','{:s}',{:f},'{:s}',dept,insee_com,nom_com,0 FROM code_cadastre WHERE insee_com = '{:s}';".format(source,etape,t,th,code_insee)
	str_query = str_query+'COMMIT;'
	# print(str_query)
	cur.execute(str_query)
	str_query = 'SELECT id_batch::integer FROM batch WHERE {:s};'.format(whereclause)
	#print(str_query)
	cur.execute(str_query)
	c = cur.fetchone()
	return c[0]
def batch_end_log(nb,batch_id):
	cur = db.bano.cursor()
	t = time.localtime()
	th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
	whereclause = 'id_batch = {:d}'.format(batch_id)
	str_query = 'UPDATE batch SET nombre_adresses = {:d},date_fin = \'{:s}\' WHERE {:s};COMMIT;'.format(nb,th,whereclause)
	cur.execute(str_query)
def age_etape_dept(etape,dept):
    cur = db.bano.cursor()
    t = time.localtime()
    t = round(time.mktime(t),0)
    str_query = 'SELECT timestamp_debut FROM batch WHERE etape = \'{:s}\' AND dept = \'{:s}\' UNION ALL SELECT 0 ORDER BY 1 DESC;'.format(etape,dept)
    cur.execute(str_query)
    c = cur.fetchone()
    return t - c[0]
def get_cadastre_format(insee):
    str_query = 'SELECT format_cadastre FROM code_cadastre WHERE insee_com = \'{:s}\';'.format(insee)
    cur = db.bano.cursor()
    cur.execute(str_query)
    for c in cur:
        code_cadastre = c[0]
    return code_cadastre
def get_cadastre_etape_timestamp_debut(code_cadastre,etape,source):
    str_query = "SELECT timestamp_debut FROM batch WHERE cadastre_com = '{:s}' AND etape = '{:s}' AND source = '{:s}';".format(code_cadastre,etape,source)
    cur = db.bano.cursor()
    cur.execute(str_query)
    for c in cur:
        code_cadastre = c[0]
    return code_cadastre

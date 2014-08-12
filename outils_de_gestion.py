#!/usr/bin/env python
# coding: UTF-8

import time
import psycopg2
from pg_connexion import get_pgc

def batch_start_log(source,etape,code_cadastre):
	t = time.localtime()
	th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
	t = round(time.mktime(t),0)
	pgc = get_pgc()
	cur = pgc.cursor()
	if len(etape)>10 and etape[0:10] == 'cache_dept':
		whereclause = 'dept = \'{:s}\' AND etape = \'{:s}\''.format(code_cadastre,etape)
	else:
		whereclause = 'cadastre_com = \'{:s}\' AND source = \'{:s}\' AND etape = \'{:s}\''.format(code_cadastre,source,etape)
	str_query = 'INSERT INTO batch_historique (SELECT * FROM batch WHERE {:s});'.format(whereclause)
	str_query = str_query+'DELETE FROM batch WHERE {:s};'.format(whereclause)
	if len(etape)>10 and etape[0:10] == 'cache_dept':
		str_query = str_query+'INSERT INTO batch (etape,timestamp_debut,date_debut,dept,nombre_adresses) SELECT \'{:s}\',{:f},\'{:s}\',\'{:s}\',0;'.format(etape,t,th,code_cadastre)
	else:
		str_query = str_query+'INSERT INTO batch (source,etape,timestamp_debut,date_debut,dept,cadastre_com,nom_com,nombre_adresses) SELECT \'{:s}\',\'{:s}\',{:f},\'{:s}\',dept,cadastre_com,nom_com,0 FROM code_cadastre WHERE cadastre_com = \'{:s}\';'.format(source,etape,t,th,code_cadastre)
	str_query = str_query+'COMMIT;'
	# print(str_query)
	cur.execute(str_query)
	str_query = 'SELECT id_batch::integer FROM batch WHERE {:s};'.format(whereclause)
	cur.execute(str_query)
	c = cur.fetchone()
	return c[0]
def batch_end_log(nb,batch_id):
	pgc = get_pgc()
	cur = pgc.cursor()
	t = time.localtime()
	th =  time.strftime('%d-%m-%Y %H:%M:%S',t)
	whereclause = 'id_batch = {:d}'.format(batch_id)
	str_query = 'UPDATE batch SET nombre_adresses = {:d},date_fin = \'{:s}\' WHERE {:s};COMMIT;'.format(nb,th,whereclause)
	# print(str_query)
	cur.execute(str_query)
def get_api_domaine_by_dept(code_dept):
        s_domaine = 'oapi-fr.openstreetmap.fr/oapi'
        s_domaine = 'api.openstreetmap.fr/oapi'
	s_domaine = 'api-fr.openstreetmap.fr/oapi'
        s_domaine = 'overpass-api.de/api'
	if code_dept[0:2] == '97':
		s_domaine = 'overpass-api.de/api'
	return s_domaine
def age_etape_dept(etape,dept):
	pgc = get_pgc()
	cur = pgc.cursor()
	t = time.localtime()
	t = round(time.mktime(t),0)
	str_query = 'SELECT timestamp_debut FROM batch WHERE etape = \'{:s}\' AND dept = \'{:s}\' UNION ALL SELECT 0 ORDER BY 1 DESC;'.format(etape,dept)
	cur.execute(str_query)
	c = cur.fetchone()
	return t - c[0]	
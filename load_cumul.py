#!/usr/bin/env python
# -*- coding: utf-8 -*-

import addr_2_db as a
import log_2_file as e
import outils_de_gestion as o
import sys
import os,os.path
import codecs

os.umask(0000)

# Wrap sys.stdout with a writer that knows how to handle encoding
# Unicode data.
wrapped_stdout = codecs.getwriter('UTF-8')(sys.stdout)
# Replace sys.stdout with a writer
sys.stdout = wrapped_stdout


def get_code_dept_from_insee(insee):
	code_dept = insee[0:2]
	if insee[0:2] == '97':
		code_dept = insee[0:3]
	return code_dept
def get_data_by_dept_from_pg(data_type,dept):
	if dept[0:1] == '0':
		dept = dept[1:]
	etape_dept = 'cache_dept_'+data_type
# Cache gardé 1h
	if o.age_etape_dept(etape_dept,dept) > 3600:
		print(u'Mise à jour du cache "{:s}"'.format(data_type.upper()))
		batch_id = o.batch_start_log(source,etape_dept,dept)
		fq = open('sql/{:s}.sql'.format(data_type),'rb')
		str_sql_dept_like = (dept+'___')[0:5]
		str_query = fq.read().replace('=\'__com__',' LIKE  \'{:s}'.format(str_sql_dept_like))
		fq.close()
		cur = pgcl.cursor()
		cur.execute(str_query)
		
		str_query_com = "SELECT insee_com,cadastre_com FROM code_cadastre WHERE dept = '{:s}'".format(dept)
		cur_com = pgc.cursor()
		cur_com.execute(str_query_com)
		k_insee = {}
		for c in cur_com:
			k_insee[c[0]] = {'cad':c[1],'data':[]}
		for lt in cur:
			l = list(lt)
			insee = l[-1]
			# Exceptions Paris/Lyon/Marseille
			if insee == '75056' or insee == '13055' or insee == '69123':
				continue
			l = l[0:-1]
			if insee not in k_insee:
				e.write_log_to_file(f_log,'Commune manquante au Cadastre : INSEE # {:s}'.format(insee))
				continue
			k_insee[insee]['data'].append(str(l))
		for k in k_insee.iterkeys():
			# print(k)
			cache_file = a.get_cache_filename(data_type,k,k_insee[k]['cad'])
			# print(cache_file)
			f = open(cache_file,'w')
			f.write('\n'.join(k_insee[k]['data']))
			f.close()
		o.batch_end_log(len(k_insee.keys()),batch_id)

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
	loop_query = 'SELECT DISTINCT cadastre_dept FROM code_cadastre ORDER BY 1;'
else:
	num_dept_cadastre = ('000'+sys.argv[1])[-3:]
	loop_query = 'SELECT \'{:s}\';'.format(num_dept_cadastre)

cur_loop = pgc.cursor()
cur_loop.execute(loop_query)
for c_loop in cur_loop:
	num_dept_cadastre = c_loop[0]
	global f_log
	f_log = e.start_log_to_file(source,os.path.basename(sys.argv[0]).split('.')[0],num_dept_cadastre)
	print(u'## Département {:s}'.format(num_dept_cadastre))
	if source == 'OSM':
		get_data_by_dept_from_pg('hsnr_insee',num_dept_cadastre)
		get_data_by_dept_from_pg('hsnr_bbox_insee',num_dept_cadastre)
		get_data_by_dept_from_pg('point_par_rue_insee',num_dept_cadastre)
		get_data_by_dept_from_pg('point_par_rue_complement_insee',num_dept_cadastre)
	# os._exit(0)
	
	get_data_by_dept_from_pg('highway_insee',num_dept_cadastre)
	get_data_by_dept_from_pg('highway_bbox_insee',num_dept_cadastre)
	get_data_by_dept_from_pg('highway_relation_insee',num_dept_cadastre)
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


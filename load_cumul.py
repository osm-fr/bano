#!/usr/bin/env python
# coding: UTF-8

# import addr_2_db as a
# import addr_osm_2_db as o
import log_2_file as e
import sys
import os,os.path

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

if source == 'CADASTRE':
	import addr_cad_2_db as a
	clause_vecteur = ' AND format_cadastre = \'VECT\' '
if source == 'OSM':
	import addr_osm_2_db as a

pgc = a.get_pgc()

if sys.argv[1] == 'FRANCE':
	loop_query = 'SELECT DISTINCT cadastre_dept FROM code_cadastre ORDER BY 1;'
else:
	num_dept_cadastre = ('000'+sys.argv[1])[-3:]
	loop_query = 'SELECT \'{:s}\';'.format(num_dept_cadastre)

cur_loop = pgc.cursor()
cur_loop.execute(loop_query)
for c_loop in cur_loop:
	num_dept_cadastre = c_loop[0]
	f_log = e.start_log_to_file(source,os.path.basename(sys.argv[0]).split('.')[0],num_dept_cadastre)

	clause_vecteur = ''
	if source == 'CADASTRE':
		clause_vecteur = ' AND format_cadastre = \'VECT\' '
	str_query = 'SELECT insee_com,cadastre_com,nom_com FROM code_cadastre WHERE cadastre_dept = \'{:s}\' {:s} ORDER BY 3;'.format(num_dept_cadastre,clause_vecteur)
	cur = pgc.cursor()
	cur.execute(str_query)
	for c in cur:
		print(c[2])
		try:
			a.main(['',c[0],c[1],source])
		except :
			e.write_log_to_file(f_log,'Commune : {:s}\n'.format(c[2]))
			e.write_log_to_file(f_log,str(sys.exc_info()[0]))
			e.write_log_to_file(f_log,str(sys.exc_info()[1]))
			e.write_sep_to_file(f_log)
	e.end_log_to_file(f_log,True)


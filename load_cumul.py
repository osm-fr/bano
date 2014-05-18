#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os

if len(sys.argv) != 3:
	print('Mauvais nombre d\'arguments')
	print('USAGE : python load_cumul.py <numero de dept> <OSM|CADASTRE>')
	os._exit(0)
source = sys.argv[2].upper()
if source != 'OSM' and source != 'CADASTRE':
	print('La source doit etre OSM ou CADASTRE')
	print('USAGE : python load_cumul.py <numero de dept> <OSM|CADASTRE>')
        os._exit(0)

num_dept_cadastre = ('000'+sys.argv[1])[-3:]

clause_vecteur = ''
if source == 'CADASTRE':
	clause_vecteur = ' AND format_cadastre = \'VECT\' '
pgc = a.get_pgc()
str_query = 'SELECT insee_com,cadastre_com,nom_com FROM code_cadastre WHERE cadastre_dept = \'{:s}\' {:s} ORDER BY 3;'.format(num_dept_cadastre,clause_vecteur)
cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	try:
		a.main(['',c[0],c[1],source])
	except ValueError:
		print('****** load KO ********')

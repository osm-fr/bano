#!/usr/bin/env python
# coding: UTF-8

import hameaux_depuis_noms_de_voies as a
import sys
import os,os.path
import subprocess

if len(sys.argv) != 2:
        print('Mauvais nombre d\'arguments')
        print('USAGE : ./detection_hameaux.py <numero de dept|FRANCE>')
        os._exit(0)

clause_where = ''
if sys.argv[1].upper() != 'FRANCE':
	num_dept_cadastre = ('000'+sys.argv[1])[-3:]
	clause_where = 'AND c.cadastre_dept = \'{:s}\''.format(num_dept_cadastre)
	
pgc = a.get_pgc()
str_query = 'SELECT DISTINCT c.insee_com,c.nom_com,c.cadastre_dept FROM code_cadastre c WHERE c.format_cadastre = \'VECT\' {:s} ORDER BY 3,2;'.format(clause_where)
cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[0]+' '+c[1])
	a.main(['','{:s}'.format(c[0])])

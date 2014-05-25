#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess

if len(sys.argv) != 1:
	print('Mauvais nombre d\'arguments')
	print('USAGE : ./import_cadastre_france.py')
	os._exit(0)

pgc = a.get_pgc()
str_query = 'SELECT insee_com,cadastre_com,nom_com,cadastre_dept FROM code_cadastre WHERE format_cadastre = \'VECT\' ORDER BY dept,nom_com;' 
#str_query = 'SELECT insee_com,cadastre_com,nom_com FROM code_cadastre WHERE cadastre_dept = \'{:s}\'  AND format_cadastre = \'VECT\' ORDER BY 3;'.format(num_dept_cadastre)
cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	if not os.path.exists('/data/work/cadastre.openstreetmap.fr/bano_cache/{:s}/{:s}/{:s}-adresses.osm'.format(c[3],c[1],c[1])):
		subprocess.call('./import-bano.sh {:s} {:s} "{:s}"  true'.format(c[3],c[1],c[2]),shell=True)
#	try:
#		subprocess.call('chmod -R g+w /data/work/cadastre.openstreetmap.fr//{:s}/{:s}'.format(num_dept_cadastre,c[1]),shell=True)
#	except:
#		"Pas de changements de droits"

#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess

if len(sys.argv) != 2:
	print('Mauvais nombre d\'arguments')
	print('USAGE : python load_cumul.py <numero de dept>')
	os._exit(0)

num_dept_cadastre = ('000'+sys.argv[1])[-3:]

pgc = a.get_pgc()
str_query = 'SELECT insee_com,cadastre_com,nom_com FROM code_cadastre WHERE cadastre_dept = \'{:s}\'  AND format_cadastre = \'VECT\' ORDER BY 3;'.format(num_dept_cadastre)
cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	if not os.path.exists('/data/work/cadastre.openstreetmap.fr/hidden/{:s}/{:s}/{:s}-adresses.osm'.format(num_dept_cadastre,c[1],c[1])):
		subprocess.call('./import-bano.sh {:s} {:s} "{:s}"  true'.format(num_dept_cadastre,c[1],c[2]),shell=True)
	subprocess.call('chmod -R g+w /data/work/cadastre.openstreetmap.fr/hidden/{:s}/{:s}'.format(num_dept_cadastre,c[1]),shell=True)

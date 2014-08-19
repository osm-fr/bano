#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
from pg_connexion import get_pgc

if len(sys.argv) != 1:
	print('Mauvais nombre d\'arguments')
	print('USAGE : ./import_cadastre_france.py')
	os._exit(0)

pgc = get_pgc()
str_query = 'SELECT insee_com,cadastre_com,nom_com,cadastre_dept FROM code_cadastre WHERE format_cadastre = \'VECT\' ORDER BY dept,nom_com;' 

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	house_fname = '/data/work/cadastre.openstreetmap.fr/bano_cache/{:s}/{:s}/{:s}-{:s}-houses.osm'.format(c[3],c[1],c[1],c[2])
	if not os.path.exists(house_fname):
		batch_id = batch_start_log('CADASTRE','importQadastre',c[1])
		subprocess.call('./qadastre.sh {:s} {:s} "{:s}"  true'.format(c[3],c[1],c[2]),shell=True)
		if not os.path.exists(house_fname):
			batch_end_log(0,batch_id)
		else:
			batch_end_log(1,batch_id)


#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess
import glob
import time
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
from pg_connexion import get_pgc

if len(sys.argv) > 2:
	print('Mauvais nombre d\'arguments')
	print('USAGE : ./import_cadastre_france.py {dept}')
	os._exit(0)

pgc = get_pgc()
if len(sys.argv) == 2:
	str_query = 'SELECT insee_com,cadastre_com,nom_com,cadastre_dept FROM code_cadastre WHERE format_cadastre = \'VECT\' AND dept = \'{:s}\' ORDER BY dept,nom_com;'.format(sys.argv[1])
else:
	str_query = 'SELECT c.insee_com,c.cadastre_com,c.nom_com,c.cadastre_dept FROM code_cadastre c LEFT OUTER JOIN (SELECT cadastre_com FROM batch WHERE etape = \'importQadastre\' AND date_fin IS NOT NULL) b ON c.cadastre_com = b.cadastre_com WHERE b.cadastre_com IS NULL AND c.format_cadastre = \'VECT\' ORDER BY dept,nom_com;' 

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	parts = glob.glob('/data/work/cadastre.openstreetmap.fr/bano_cache/{:s}/{:s}/{:s}-[0-9]-[0-9].pdf'.format(c[3],c[1],c[1]))
	nb_parts = len(parts)
	batch_id = batch_start_log('CADASTRE','importQadastre',c[1])
	for p in parts:
		# print(p)
		p_out = p[0:-4]+'-houses.osm'
		p_out_city = p[0:-4]+'-city-limit.osm'
		p_out_water = p[0:-4]+'-water.osm'
		suffixe = '-'.join(p[0:-4].rsplit('-',2)[1:])
		if not (os.path.exists(p_out) or os.path.exists(p_out_city) or os.path.exists(p_out_water) ):
			print(p_out)
			subprocess.call('./qadastre.sh {:s} {:s} "{:s}"'.format(c[3],c[1],suffixe),shell=True)
			if not os.path.exists(p_out):
				nb_parts -=1
		# os._exit(0)
	batch_end_log(nb_parts,batch_id)
	time.sleep(1)
	# os._exit(0)

#!/usr/bin/env python
# coding: UTF-8

import sys
import os,os.path
import subprocess
import glob
import time
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
from pg_connexion import get_pgc

if len(sys.argv) > 1:
	print('USAGE : ./convert_qadastre_2_osm_differentiel.py')
	os._exit(0)

pgc = get_pgc()
str_query = "SELECT DISTINCT c.insee_com,c.cadastre_com,c.nom_com,c.cadastre_dept FROM code_cadastre c JOIN (SELECT cadastre_com FROM code_cadastre  WHERE format_cadastre = 'VECT' EXCEPT SELECT b1.cadastre_com FROM batch b1 JOIN batch b2 USING (cadastre_com) WHERE b1.etape = 'importQadastre' AND b2.etape = 'recupCadastre' AND b1.timestamp_debut > b2.timestamp_debut AND b1.date_fin IS NOT NULL AND b2.date_fin IS NOT NULL) j USING (cadastre_com) ORDER BY 4,3;"

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	parts = glob.glob('/data/work/cadastre.openstreetmap.fr/bano_cache/{:s}/{:s}/{:s}-[0-9]-[0-9].pdf'.format(c[3],c[1],c[1]))
	nb_parts = len(parts)
	batch_id = batch_start_log('CADASTRE','importQadastre',c[1])
	for p in parts:
		p_out = p[0:-4]+'-houses.osm'
		suffixe = '-'.join(p[0:-4].rsplit('-',2)[1:])
		print(suffixe)
		subprocess.call('./qadastre_convert.sh {:s} {:s} "{:s}"'.format(c[3],c[1],suffixe),shell=True)
		if not os.path.exists(p_out):
			nb_parts -=1
	batch_end_log(nb_parts,batch_id)
	time.sleep(1)

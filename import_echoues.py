#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess

if len(sys.argv) != 2:
        print('Mauvais nombre d\'arguments')
        print('USAGE : ./import_echoues.py <numero de dept>')
        os._exit(0)

num_dept_cadastre = ('000'+sys.argv[1])[-3:]

pgc = a.get_pgc()
str_query = 'SELECT c.insee_com,c.cadastre_com,c.nom_com FROM code_cadastre c LEFT OUTER JOIN (SELECT * FROM batch WHERE etape = \'recupCadastre\' AND nombre_adresses = -1) b ON c.dept = b.dept AND c.cadastre_com = b.cadastre_com WHERE c.cadastre_dept = \'{:s}\' AND c.format_cadastre = \'VECT\' AND b.cadastre_com IS NULL  ORDER BY 3;'.format(num_dept_cadastre)
cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
#	if not os.path.exists('/data/work/cadastre.openstreetmap.fr/bano_cache/{:s}/{:s}/{:s}-adresses.osm'.format(num_dept_cadastre,c[1],c[1])):
	subprocess.call('./import-bano.sh {:s} {:s} "{:s}"  true'.format(num_dept_cadastre,c[1],c[2]),shell=True)
#	try:
#		subprocess.call('chmod -R g+w /data/work/cadastre.openstreetmap.fr//{:s}/{:s}'.format(num_dept_cadastre,c[1]),shell=True)
#	except:
#		"Pas de changements de droits"

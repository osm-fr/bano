#!/usr/bin/env python
# coding: UTF-8

import addr_2_db as a
import sys
import os,os.path
import subprocess

if len(sys.argv) != 1:
        print('Mauvais nombre d\'arguments')
        print('USAGE : ./import_echoues_france.py')
        os._exit(0)

pgc = a.get_pgc()
str_query = 'SELECT c.insee_com,c.cadastre_com,c.nom_com,c.cadastre_dept FROM code_cadastre c LEFT OUTER JOIN (SELECT * FROM batch WHERE etape = \'recupCadastre\' AND nombre_adresses = -1) b ON c.dept = b.dept AND c.cadastre_com = b.cadastre_com WHERE c.format_cadastre = \'VECT\' AND b.cadastre_com IS NULL  ORDER BY 4,3;'

cur = pgc.cursor()
cur.execute(str_query)
for c in cur:
	print(c[2])
	subprocess.call('./import-bano.sh {:s} {:s} "{:s}"  true'.format(c[3],c[1],c[2]),shell=True)

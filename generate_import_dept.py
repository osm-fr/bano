#!/usr/bin/env python
# coding: UTF-8
import os
import psycopg2
from pg_connexion import get_pgc

pgc = get_pgc()
cur_dept = pgc.cursor()
cur_comm = pgc.cursor()

str_query = 'SELECT DISTINCT dept FROM code_cadastre WHERE dept IS NOT NULL;'
# str_query = 'SELECT DISTINCT dept FROM code_cadastre WHERE dept =\'090\';'
cur_dept.execute(str_query)
for d in cur_dept:
	str_query = 'SELECT cadastre_com,nom_com FROM code_cadastre WHERE dept = \'{:s}\' ORDER BY 1;'.format(d[0])
	cur_comm.execute(str_query)
	fn = 'import_v2_{:s}.sh'.format(d[0])
	f = open(fn,'wb')
	f.write('#!/bin/bash\n')
	f.write('cd /data/project/cadastre.openstreetmap.fr/export-cadastre/bin/cadastre-housenumber/bano\n')
	for c in cur_comm:
		f.write('./import-bano.sh {:s} {:s} "{:s}" true\n'.format(d[0],c[0],c[1]))
	f.close()
	os.chmod(fn,0777)

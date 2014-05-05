# encoding:UTF-8
import psycopg2
from pg_connexion import get_pgc
import os, os.path
import sys
import glob

filter = '*'
if len(sys.argv) == 2:
		filter = sys.argv[1]

pgc = get_pgc()
cur = pgc.cursor()

for f in sorted(glob.glob('fantoir/*'+filter+'*.txt')):
		print(f)
		h = open(f,'r')
		l1 = h.readline()
		dept = l1[0:2]
		dir = l1[2:3]
		a_rows = []
		if dept == '97':
			str_query = '''DELETE FROM fantoir_voie WHERE code_dept = \''''+dept+'''\' AND code_dir = \''''+dir+'''\';'''
		else:
			str_query = '''DELETE FROM fantoir_voie WHERE code_dept = \''''+dept+'''\';'''
		cur.execute(str_query)
		str_query = '''INSERT INTO fantoir_voie VALUES '''
		for i,l in enumerate(h):
		# enregistrement != Voie
				if l[6:7].rstrip() == '':
								continue
				#print(l)
				a_rows.append([l[0:2],l[2:3],l[3:6],l[0:2]+l[3:6],l[6:10],l[10:11],l[11:15].rstrip(),l[15:41].rstrip().replace("'", r"''"),l[42:43],l
[45:46],l[48:49],l[49:50].rstrip(),l[59:66],l[66:73],l[73:74].rstrip(),l[74:81],l[81:88],l[103:108],l[108:109],l[109:110].rstrip(),l[112:120].rstrip()])
				if i%1000 == 0:
						for r in a_rows:
								str_query = str_query+'(\''+("','").join(r)+'\'),'
						str_query = str_query.rstrip(',')+';commit;'
						cur.execute(str_query)
						str_query = '''INSERT INTO fantoir_voie VALUES '''
						a_rows = []
		if len(a_rows) > 0:
				for r in a_rows:
						str_query = str_query+'(\''+("','").join(r)+'\'),'
				str_query = str_query.rstrip(',')+';commit;'
				cur.execute(str_query)


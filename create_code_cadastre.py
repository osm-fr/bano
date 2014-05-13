#!/usr/bin/env python
# coding: UTF-8

# Version rapide de récup des codes Cadastre communaux à partir des csv
# générés ici : http://suivi.openstreetmap.fr/communes/stats-cadastre/
# liste à vérifier / compléter / méthode à revoir

import urllib2
import os

outfile = open('code_cadastre.csv','wb')
dict_codes_cadastre = {}

a_depts = ['2A','2B']
for n in range(1,20)+range(21,96)+range(971,975):
	a_depts.append(str(n).rjust(2,'0'))

for d in a_depts:
	url = 'http://suivi.openstreetmap.fr/communes/stats-cadastre/{:s}.csv'.format(d)
	try:
		r = urllib2.urlopen(url)
#		s = r.read()
		for line in r:
			code_cadastre = line.split(',')[2]
#			print(line)
#			print(line.split(','))
#			os._exit(0)
			if code_cadastre not in dict_codes_cadastre:
				outfile.write(('{:s},{:s},{:s}').format(d,d.rjust(3,'0'),line))
				dict_codes_cadastre[code_cadastre]=1
	except urllib2.HTTPError:
		print ('*** Echec sur {:s}'.format(url))

outfile.close()


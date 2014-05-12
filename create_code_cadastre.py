# Version rapide de récup des codes Cadastre communaux à partir des csv
# générés ici : http://suivi.openstreetmap.fr/communes/stats-cadastre/
# liste à vérifier / compléter / méthode à revoir

import urllib2

outfile = open('code_cadastre.csv','wb')

a_depts = ['2A','2B']
for n in range(1,20)+range(21,96)+range(971,975):
	a_depts.append(str(n).rjust(2,'0'))

for d in a_depts:
	url = 'http://suivi.openstreetmap.fr/communes/stats-cadastre/{:s}.csv'.format(d)
	try:
		r = urllib2.urlopen(url)
		s = r.read()
		outfile.write(s)
	except urllib2.HTTPError:
		print ('*** Echec sur {:s}'.format(url))

outfile.close()


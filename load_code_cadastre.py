#!/usr/bin/env python
# coding: UTF-8

import urllib, urllib2, cookielib
import time
import os
import xml.etree.ElementTree as ET

a_depts = ['2A','2B']
for n in range(1,20)+range(21,96)+range(971,975):
        a_depts.append(str(n).rjust(2,'0'))
a_0_depts = [a.rjust(3,'0') for a in a_depts]
f_output = open('code_cadastre.csv','wb')
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
request = urllib2.Request('http://www.cadastre.gouv.fr/scpc/rechercherPlan.do')
for i,d in enumerate(a_0_depts):
	fname = 'dept_'+a_0_depts[i]+'.xml'
	time.sleep(1)
	opener.open(request)
	request = urllib2.Request('http://www.cadastre.gouv.fr/scpc/listerCommune.do?codeDepartement='+d+'&libelle=&keepVolatileSession=&offset=5000')
	response = opener.open(request)
	rep = response.read()
	fw = open(fname,'wb')
	fw.write(rep)
	fw.close()
	fr = open(fname,'r')
	for line in fr:
		lsplit = line.split('listerFeuillesParcommune')
		lsplit = line.split('ajoutArticle(')
		if len(lsplit) > 1:
			code_commune = lsplit[1][1:6]
			format = lsplit[1][9:13]
			commune_cp = lsplit[0].split('td class="nom"')[1].split('feuille')[0].split('strong')[1]
			nom_commune = commune_cp[1:-11]
			cp = commune_cp[-9:-4]
			# print(code_commune,format,nom_commune,cp)
			f_output.write('{:s},{:s},{:s},{:s},{:s},{:s}\n'.format(a_depts[i],d,nom_commune,cp,code_commune,format))
		f_output.flush()
	fr.close()
	os.remove(fname)
f_output.close()


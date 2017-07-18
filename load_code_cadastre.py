#!/usr/bin/env python
# coding: UTF-8

import urllib2
import cookielib
import time
import os
from bs4 import BeautifulSoup
import re

a_depts = []
for n in range(1, 20)+['2A', '2B']+range(21, 96)+range(971, 975) + [976]:
    a_depts.append(str(n).rjust(2, '0'))
a_0_depts = [a.rjust(3, '0') for a in a_depts]
f_output = open('code_cadastre.csv', 'wb')
cookieJar = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar))
request = urllib2.Request(
    'https://www.cadastre.gouv.fr/scpc/rechercherPlan.do')
response = opener.open(request)
token = response.read().split('CSRF_TOKEN=')[1].split('"')[0]

COMMUNE_CP_REGEX = re.compile('^(.*?) \((.*?)\) $')

for i, d in enumerate(a_0_depts):
    fname = 'dept_'+d+'.xml'
    time.sleep(1)
    opener.open(request)
    request2 = urllib2.Request(
        "https://www.cadastre.gouv.fr/scpc/listerCommune.do?CSRF_TOKEN={:s}&codeDepartement={:s}&libelle=&keepVolatileSession=&offset=5000".format(token, d))
    response = opener.open(request2)
    rep = response.read()
    fw = open(fname, 'wb')
    fw.write(rep)
    fw.close()
    fr = BeautifulSoup(open(fname, 'r').read(), "lxml")

    for e in fr.find_all(attrs={"class": "parcelles"}):
        y = e.find(title="Ajouter au panier")
        if y is None:
            continue

        # y.get('onclick') structure: "ajoutArticle('CL098','VECT','COMU');"
        split = y.get('onclick').split("'")
        code_commune = split[1]
        format_type = split[3]

        # e.strong.string structure: "COBONNE (26400) "
        commune_cp = e.strong.string
        (nom_commune, cp) = COMMUNE_CP_REGEX.match(commune_cp).group(1, 2)

        f_output.write('{:s},{:s},{:s},{:s},{:s},{:s}\n'.format(
            a_depts[i], d, nom_commune, cp, code_commune, format_type))
        f_output.flush()
    os.remove(fname)
f_output.close()

#!/usr/bin/env python

import urllib.request
from http.cookiejar import CookieJar
import time
import os
from bs4 import BeautifulSoup

a_depts = []
for n in list(range(1, 20))+['2A', '2B']+list(range(21, 96))+list(range(971, 975)) + [976]:
    a_depts.append(str(n).rjust(2, '0'))
a_0_depts = [a.rjust(3, '0') for a in a_depts]
f_output = open('code_cadastre.csv', 'w')
cookiejar = CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookiejar))
request = urllib.request.Request(
    'https://www.cadastre.gouv.fr/scpc/rechercherPlan.do')
response = opener.open(request)
token = response.read().decode().split('CSRF_TOKEN=')[1].split('"')[0]

for i, d in enumerate(a_0_depts):
    fname = 'dept_'+d+'.xml'
    time.sleep(1)
    opener.open(request)
    request2 = urllib.request.Request(
        "https://www.cadastre.gouv.fr/scpc/listerCommune.do?CSRF_TOKEN={:s}&codeDepartement={:s}&libelle=&keepVolatileSession=&offset=5000".format(token, d))
    response = opener.open(request2)
    rep = response.read()
    fw = open(fname, 'wb')
    fw.write(rep)
    fw.close()
    fr = BeautifulSoup(open(fname, 'rb').read(), "lxml")

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
        nom_commune = commune_cp[:-9]
        cp = commune_cp[-7:-2]
        # try: 
        f_output.write('{:s},{:s},{:s},{:s},{:s},{:s}\n'.format(
                a_depts[i], d, nom_commune, cp, code_commune, format_type))
        # except:
            # import pdb; pdb.Pdb().set_trace()
        f_output.flush()
    os.remove(fname)
f_output.close()

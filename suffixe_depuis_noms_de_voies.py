#!/usr/bin/env python
# coding: UTF-8

import re
import sys
import time
import os,os.path
from pg_connexion import get_pgc
from pg_connexion import get_pgc_osm
# from addr_2_db import load_cadastre_hsnr
from addr_2_db import get_code_cadastre_from_insee
from addr_2_db import get_short_code_dept_from_insee
from addr_2_db import get_nb_parts
from addr_2_db import get_part_debut
from addr_2_db import get_tags
from addr_2_db import is_valid_housenumber
from addr_2_db import Node
from addr_2_db import Adresse
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import xml.etree.ElementTree as ET

class Adresses:
    def __init__(self):
        self.a = {}
    def register(self,voie):
        cle = normalize(voie)
        if not cle in self.a:
            self.a[cle] = {'numeros':{},'voies':{},'fantoirs':{}}
    def add_fantoir(self,cle,fantoir,source):
        self.register(cle)
        if len(fantoir) == 10:
            self.a[cle]['fantoirs'][source] = fantoir
        else:
            print(u'Code Fantoir non conforme : {:s}'.format(fantoir))
    def add_voie(self,voie,source):
        cle = normalize(voie)
        self.a[cle]['voies'][source] = voie
    def add_adresse(self,ad,source):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        if (ad.fantoir == '' or (is_valid_fantoir(ad.fantoir) and ad.fantoir[0:5] == code_insee)) and is_valid_housenumber(ad.numero):
            cle = normalize(ad.voie)
            self.add_voie(ad.voie,source)
            self.a[cle]['numeros'][ad.numero] = ad
            if ad.fantoir != '':
                self.a[cle]['fantoirs']['OSM'] = ad.fantoir
        else:
            print(u'adresse rejetée : {:s} {:s}'.format(ad.numero,ad.fantoir))
    def get_cle_by_fantoir(self,fantoir):
        cle = ''
        for c in self.a:
            if 'fantoirs' in self.a[c]:
                if 'OSM' in self.a[c]['fantoirs']:
                    if self.a[c]['fantoirs']['OSM'] == fantoir:
                        cle = c
                        break
                if 'FANTOIR' in self.a[c]['fantoirs']:
                    if self.a[c]['fantoirs']['FANTOIR'] == fantoir:
                        cle = c
                        break
        return cle
    def has_already_fantoir(self,cle,source):
        has = False
        if source in self.a[cle]['fantoirs']:
            has = True
        return has
def collect_adresses_points(sel):
    kres = {}
    for k in sel:
        kres[k] = []
        for vv in sel[k]['liste']:
            s = 0
            max = 2
            for a in adresses.a[vv]['numeros']:
                kres[k].append('SELECT \'{:s}\' hameau,\'{:s}\' code_insee,ST_BUFFER(ST_PointFromText(\'POINT({} {})\',4326),0.0003,2) as g'.format(k.replace("'","''"),code_insee,adresses.a[vv]['numeros'][a].node.attribs['lon'],adresses.a[vv]['numeros'][a].node.attribs['lat']))
                s+=1
                if s == max: break
    return kres
def load_suffixe_2_db(adds):
    nb_res = 0
    cur = pgc.cursor()
    str_query = "DELETE FROM suffixe WHERE insee_com = '{:s}';COMMIT;".format(code_insee)
    cur.execute(str_query)
    for h in adds:
        # Agde (34003): detection de 'Mer' abusif, pas d'autres suffixes dans la commune
        if code_insee == '34003':
            continue
        print('\t{:s}'.format(h))
        str_query = 'INSERT INTO suffixe SELECT ST_Transform(ST_SetSRID((ST_Dump(gu)).geom,4326),3857),code_insee,hameau FROM (SELECT ST_Union(g) gu,code_insee,hameau FROM({:s})a GROUP BY 2,3)a;COMMIT;'.format(' UNION ALL '.join(adds[h]))
        cur.execute(str_query)
        nb_res+=len(adds[h])
    return nb_res
def load_hsnr_from_cad_file_csv(fnadresses,source):
    csvadresses = open(fnadresses,'r')
    dict_node_relations = {}
    for l in csvadresses:
        line_split = l.split(';')
        # cle_interop,housenumber,name,lon,lat = line_split[0],line_split[2]+line_split[3],line_split[5].decode('utf8'),line_split[13],line_split[14]
        cle_interop,housenumber,name,lon,lat = line_split[0],line_split[2]+line_split[3],line_split[5],line_split[13],line_split[14]

        if len(name) < 2:
            continue
        if len(lon) < 1:
            continue
        adresses.register(name)
        adresses.add_voie(name,'CADASTRE')
        if not cle_interop in dict_node_relations:
            dict_node_relations[cle_interop] = []
            dict_node_relations[cle_interop].append(normalize(name))
        if is_valid_housenumber(housenumber):
            nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
            adresses.add_adresse(Adresse(nd,housenumber,name,'',''),source)
def load_cadastre_hsnr(code_insee):
    dict_node_relations = {}
    destinations_principales_retenues = 'habitation commerce industrie tourisme'
    str_query = "SELECT * FROM bal_cadastre WHERE commune_code = '{}';".format(code_insee)
    cur_bal = pgc_osm.cursor()
    cur_bal.execute(str_query)
    for lt in cur_bal:
        line_split = list(lt)
        cle_interop,housenumber,pseudo_adresse,name,code_postal,destination_principale,lon,lat = line_split[0],line_split[2]+(str(line_split[3]) if (line_split[3]) else ''),line_split[4],line_split[5],(line_split[7] if line_split[7] else ''),line_split[9],line_split[13],line_split[14]
        if len(name) < 2:
            continue
        # if len(lon) < 1:
        if not lon :
            continue
        if pseudo_adresse == 'true':
            continue
        if not re.search(destination_principale,destinations_principales_retenues):
            continue
        adresses.register(name)
        adresses.add_voie(name,'CADASTRE')
        if not cle_interop in dict_node_relations:
            dict_node_relations[cle_interop] = []
            dict_node_relations[cle_interop].append(normalize(name))
        if is_valid_housenumber(housenumber):
            nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
            adresses.add_adresse(Adresse(nd,housenumber,name,'',code_postal),source)
    cur_bal.close()
def name_frequency():
    freq = {}
    for v in adresses.a:
        s = v.split()
        if len(s)>4:
            k = ' '.join(s[-2:])
            if k not in freq:
                freq[k] = {'nombre':1,'liste':[v]}
            else:
                freq[k]['nombre'] +=1
                freq[k]['liste'].append(v)
        if len(s)>3:
            k = v.split()[-1]
            if k not in freq:
                freq[k] = {'nombre':1,'liste':[v]}
            else:
                freq[k]['nombre'] +=1
                freq[k]['liste'].append(v)
    return freq
def normalize(s):

    return s
def select_street_names_by_name(freq):
    sel = {}
    mots = {}
    for k in freq:
        ks = k.split()
        if freq[k]['nombre'] > 5 and len(ks) > 1:
            mots[ks[0]] = 1
            mots[ks[1]] = 1
            sel[k] = freq[k]
    for k in freq:
        ks = k.split()
        # un suffixe ne peut pas être un numero seul, cas dans les arrdts parisiens
        if freq[k]['nombre'] > 5 and len(ks) == 1 and not k.isdigit() and not k in mots :
            sel[k] = freq[k]
    return sel
def main(args):
    debut_total = time.time()
    usage = 'USAGE : python suffixe_depuis_noms_de_voies.py <code INSEE>'
    if len(args) != 2:
        print(usage)
        os._exit(0)

    global pgc,pgc_osm,dicts,adresses,source,code_insee
    pgc = get_pgc()
    pgc_osm = get_pgc_osm()
    source = 'CADASTRE'
    adresses = Adresses()
    code_insee = args[1]
    code_cadastre = get_code_cadastre_from_insee(code_insee)
    code_dept = get_short_code_dept_from_insee(code_insee)

    batch_id = batch_start_log(source,'detectesuffixe',code_insee)

    # fnadresses = os.path.join(os.environ['BANO_CACHE_DIR'],code_dept,code_insee,'{}-bal.csv'.format(code_insee))
    # if (os.path.exists(fnadresses)):
    #     # load_hsnr_from_cad_file_csv(fnadresses, 'CADASTRE')
    load_cadastre_hsnr(code_insee)
    freq = name_frequency()
    sel = select_street_names_by_name(freq)
    adds = collect_adresses_points(sel)
    nb_rec = load_suffixe_2_db(adds)

    batch_end_log(nb_rec,batch_id)

if __name__ == '__main__':
    main(sys.argv)

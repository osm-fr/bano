#!/usr/bin/env python
# coding: UTF-8
from pg_connexion import get_pgc
from pg_connexion import get_pgc_layers
from outils_de_gestion import batch_start_log
from outils_de_gestion import batch_end_log
import os,os.path
import sys
import time
import xml.etree.ElementTree as ET

os.umask(0000)

class Adresse:
    def __init__(self,node,num,voie,fantoir,code_postal):
        self.node = node
        self.numero = num
        self.voie = voie
        self.fantoir = fantoir
        self.code_postal = code_postal

class Adresses:
    def __init__(self):
        self.a = {}

    def register(self,voie):
        cle = normalize(voie)
        if not cle in self.a:
            self.a[cle] = {'numeros':{},'voies':{},'fantoirs':{},'point_par_rue':[],'highway_index':0}

    def add_fantoir(self,cle,fantoir,source):
        self.register(cle)
        if len(fantoir) == 10:
            self.a[cle]['fantoirs'][source] = fantoir

    def add_voie(self,voie_cle,source,voie=None):
        cle = normalize(voie_cle)
        if not voie:
            voie = voie_cle
        self.a[cle]['voies'][source] = voie

    def add_adresse(self,ad,source):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        if (ad.fantoir == '' or (is_valid_fantoir(ad.fantoir) and ad.fantoir[0:5] == code_insee)) and is_valid_housenumber(ad.numero):
            cle = normalize(ad.voie)
            self.add_voie(ad.voie,source)
            self.a[cle]['numeros'][ad.numero] = ad
            if ad.fantoir != '':
                self.a[cle]['fantoirs']['OSM'] = ad.fantoir

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

    def add_highway_index(self,cle,val):
        self.a[cle]['highway_index']+=val

class Dicts:
    def __init__(self):
        self.lettre_a_lettre = {}
        self.fantoir = {}
        self.code_fantoir_vers_nom_fantoir = {}
        self.code_fantoir_vers_noms = {}
        self.osm_insee = {}
        self.abrev_type_voie = {}
        self.expand_noms = []
        self.expand_titres = []
        self.abrev_titres = []
        self.substitution_complete = {}
        self.chiffres = []
        self.chiffres_romains = {}
        self.mot_a_blanc = []
        self.noms_voies = {}
        self.ways_osm = {}
        self.highway_types = {}

    def load_lettre_a_lettre(self):
        self.lettre_a_lettre = {'A':[u'Â',u'À'],
                        'C':[u'Ç'],
                        'E':[u'È',u'Ê',u'É',u'Ë'],
                        'I':[u'Ï',u'Î'],
                        'O':[u'Ö',u'Ô'],
                        'U':[u'Û',u'Ü'],
                        'OE':[u'Œ']}

    def load_fantoir(self,insee):
        str_query = ("""SELECT *
                        FROM    (SELECT code_insee||id_voie||cle_rivoli,
                                        nature_voie||' '||libelle_voie,
                                        rank() OVER(PARTITION BY nature_voie||' '||libelle_voie ORDER BY type_voie,id_voie,cle_rivoli) rang
                                FROM    fantoir_voie
                                WHERE    code_insee = '%s' AND
                                        caractere_annul NOT IN ('O','Q')) a
                        WHERE rang = 1;""" % insee)
        pgc = get_pgc()
        cur_fantoir = pgc.cursor()
        cur_fantoir.execute(str_query)
        for c in cur_fantoir:
            self.code_fantoir_vers_nom_fantoir[c[0]] = c[1]
            cle = ' '.join(c[1].replace('-',' ').split())
            cle = normalize(cle)
            self.fantoir[cle] = c[0]

    def load_addr_from_fantoir(self):
        for k in self.fantoir:
            adresses.add_fantoir(k,self.fantoir[k],'FANTOIR')

    def load_chiffres(self):
        self.chiffres = [    ['0','ZERO'],
                            ['1','UN'],
                            ['2','DEUX'],
                            ['3','TROIS'],
                            ['4','QUATRE'],
                            ['5','CINQ'],
                            ['6','SIX'],
                            ['7','SEPT'],
                            ['8','HUIT'],
                            ['9','NEUF'],
                            [' DIX NEUF ',' UNNEUF '],
                            [' DIX ',' UNZERO '],
                            [' ONZE ',' UNUN '],
                            [' DOUZE ',' UNDEUX '],
                            [' TREIZE ',' UNTROIS '],
                            [' QUATORZE ',' UNQUATRE ']]

    def load_mot_a_blanc(self):
        self.mot_a_blanc = ['DE LA',
                            'DU',
                            'DES',
                            'LE',
                            'LA',
                            'LES',
                            'DE',
                            'D',
                            'L']

    def load_expand_titres(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','expand_titres.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.expand_titres.append(c)
        f.close()

    def load_expand_noms(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','expand_noms.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.expand_noms.append(c)
        f.close()

    def load_abrev_titres(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_titres.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.abrev_titres.append(c)
        f.close()

    def load_chiffres_romains(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','chiffres_romains.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.chiffres_romains[c[0]] = c[1]
        f.close()

    def load_abrev_type_voie(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','abrev_type_voie.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.abrev_type_voie[c[0]] = c[1]
        f.close()

    def load_substitution_complete(self):
        fn = os.path.join(os.path.dirname(__file__),'dictionnaires','substitution_complete.txt')
        f = open(fn)
        for l in f:
            if l[0:1] == '#':
                continue
            c = (l.splitlines()[0]).split('\t')
            self.substitution_complete[c[0]] = c[1]
        f.close()

    def load_highway_types(self):
        str_query = '''    SELECT     tag_index,
                                tag_value
                        FROM    type_voie
                        ORDER BY    tag_index;'''
        pgc = get_pgc()
        cur_hw = pgc.cursor()
        cur_hw.execute(str_query)
        for c in cur_hw:
            self.highway_types[c[1]] = c[0]

    def load_all(self,code_insee_commune):
        self.load_lettre_a_lettre()
        self.load_abrev_type_voie()
        self.load_expand_noms()
        self.load_expand_titres()
        self.load_abrev_titres()
        self.load_chiffres()
        self.load_chiffres_romains()
        self.load_mot_a_blanc()
        self.load_substitution_complete()
        self.load_fantoir(code_insee_commune)
        self.load_highway_types()

    def add_voie(self,origine,nom):
        cle = normalize(nom)
        if not cle in self.noms_voies:
            self.noms_voies[cle] = {}
        self.noms_voies[cle][origine] = nom

    def add_fantoir_name(self,fantoir,name,source):
        if not fantoir in self.code_fantoir_vers_noms:
            self.code_fantoir_vers_noms[fantoir] = {}
        if not source in self.code_fantoir_vers_noms[fantoir]:
            self.code_fantoir_vers_noms[fantoir][source] = name

    def get_fantoir_name(self,fantoir,source):
        res = ''
        if fantoir in self.code_fantoir_vers_noms:
            if source in self.code_fantoir_vers_noms[fantoir]:
                res = self.code_fantoir_vers_noms[fantoir][source]
        return res

class Node:
    def __init__(self,attribs,tags):
        self.attribs = attribs
        self.tags = tags
        self.sent = False
        self.modified = False

    def get_geom_as_text(self):
        strp = 'ST_PointFromText(\'POINT('+str(self.attribs['lon'])+' '+str(self.attribs['lat'])+')\',4326)'
        return strp

    def move_to(self,lon,lat):
        self.attribs['lon'] = lon
        self.attribs['lat'] = lat

    def get_as_osm_xml_node(self):
        s = "\t<node id="+XSS.quoteattr(self.attribs['id'])
        if self.modified:
            s = s+" action=\"modify\" "
        for a in self.attribs:
            if a != 'id':
                if a == 'user':
                    v = XSS.quoteattr(self.attribs[a]).encode('utf8')
                else:
                    v = XSS.quoteattr(str(self.attribs[a]).encode('utf8'))
                s = s+" "+a+"="+v
        if len(self.tags) == 0:
            s = s+"/>\n"
        else:
            s = s+">\n"
            for k in sorted(self.tags.viewkeys()):
                s = s+"\t\t<tag k="+XSS.quoteattr(k)+" v="+XSS.quoteattr(self.tags[k]).encode('utf8')+"/>\n"
            s = s+"\t</node>\n"
        return s

class Pg_hsnr:
    def __init__(self,d):
        self.x = d[0]
        self.y = d[1]
        self.provenance = d[2]
        self.osm_id = d[3]
        self.numero = d[4]
        self.voie = d[5]
        self.tags = tags_list_as_dict(d[6])
        self.fantoir = ''
        if self.provenance == '3' or self.provenance == '4':
            self.set_street_name()
        self.set_fantoir()
        self.code_postal = find_cp_in_tags(self.tags)

    def set_street_name(self):
        if 'type' in self.tags and self.tags['type'] == 'associatedStreet' and 'name' in self.tags:
            self.voie = self.tags['name']

    def set_fantoir(self):
        if 'ref:FR:FANTOIR' in self.tags and len(self.tags['ref:FR:FANTOIR']) == 10 and self.tags['ref:FR:FANTOIR'][0:5] == code_insee:
            self.fantoir = self.tags['ref:FR:FANTOIR']

def find_cp_in_tags(tags):
    code_postal = ''
    if 'addr:postcode' in tags : code_postal = tags['addr:postcode']
    if code_postal == '' and 'postal_code' in tags : code_postal = tags['postal_code']
    return code_postal
    
def add_fantoir_to_hsnr():
    for v in adresses.a:
        if v in dicts.fantoir:
            adresses.a[v]['fantoirs']['FANTOIR'] = dicts.fantoir[v]
            adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[dicts.fantoir[v]]
        else:
            if 'OSM' in adresses.a[v]['fantoirs']:
                if adresses.a[v]['fantoirs']['OSM'] in dicts.code_fantoir_vers_nom_fantoir:
                    adresses.a[v]['voies']['FANTOIR'] = dicts.code_fantoir_vers_nom_fantoir[adresses.a[v]['fantoirs']['OSM']]

def append_suffixe(name,suffixe):
    res = name
    if suffixe:
        name_norm = normalize(name)
        suffixe_norm = normalize(suffixe)
        ln = len(name_norm)
        ls = len(suffixe)
        if ln > ls:
            if name[-ls:] != suffixe:
                res = name+' '+suffixe
        else:
            res = name+' '+suffixe
    return res

def get_best_fantoir(cle):
    res = ''
    if 'FANTOIR' in adresses.a[cle]['fantoirs']:
        res = adresses.a[cle]['fantoirs']['FANTOIR']
    if 'OSM' in adresses.a[cle]['fantoirs']:
        res = adresses.a[cle]['fantoirs']['OSM']
    return res

def get_cache_filename(data_type,insee_com):
    code_dept = get_short_code_dept_from_insee(insee_com)
    cache_dir = os.path.join(os.environ['BANO_CACHE_DIR'],code_dept,insee_com)
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_filename = os.path.join(cache_dir,'{:s}-{:s}.csv'.format(insee_com,data_type))
    return cache_filename

def get_cadastre_code_dept_from_insee(insee):
    code_dept = '0'+insee[0:2]
    if insee[0:2] == '97':
        code_dept = insee[0:3]
    return code_dept

def get_short_code_dept_from_insee(insee):
    code_dept = insee[0:2]
    if insee[0:2] == '97':
        code_dept = insee[0:3]
    return code_dept

def get_code_cadastre_from_insee(insee):
    str_query = 'SELECT cadastre_com FROM code_cadastre WHERE insee_com = \'{:s}\';'.format(insee)
    code_cadastre = []
    pgc = get_pgc()
    cur = pgc.cursor()
    cur.execute(str_query)
    for c in cur:
        code_cadastre = c[0]
    return code_cadastre

def get_data_from_pg(data_type,insee_com,local=False,suffixe_data=None):
    cache_file = get_cache_filename(data_type,insee_com)
    if not use_cache or not os.path.exists(cache_file) or (time.time() - os.path.getmtime(cache_file)) > 86400 :
        fq = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(data_type)),'r')
        str_query = fq.read().replace('__com__',insee_com)
        fq.close()
        if local:
            pgc = get_pgc()
        else:
            pgc = get_pgc_layers()
        if suffixe_data:
            str_query = str_query.replace('__suffixe_data__',suffixe_data)
        cur = pgc.cursor()
        cur.execute(str_query)
        f = open(cache_file,'w+')
        for lt in cur:
            l = list(lt)
            f.write(str(l)+'\n')
        cur.close()
        f.seek(0)
    else :
        f = open(cache_file,'r')
    res = []
    for l in f:
        res.append(eval(l))
    f.close()
    return res

def get_geom_suffixes(insee):
    data = get_data_from_pg('geom_suffixes_insee',insee,True)
    a_queries = []
    for l in data:
        a_queries.append('SELECT ST_PolygonFromText(\'{:s}\',3857) as geom,\'{:s}\'::text suffixe'.format(l[0],l[1].replace('\'','\'\'')))
    return ' UNION '.join(a_queries)

def get_nb_parts(s):
    return len(s.split())

def get_part_debut(s,nb_parts):
    resp = ''
    if get_nb_parts(s) > nb_parts:
        resp = ' '.join(s.split()[0:nb_parts])
    return resp

def get_tags(xmlo):
    dtags = {}
    for tg in xmlo.iter('tag'):
        dtags[tg.get('k')] = tg.get('v')
    return dtags

def has_addreses_with_suffix(insee):
    res = False
    str_query = 'SELECT count(*) FROM suffixe where insee_com = \'{:s}\';'.format(insee)
    cur = pgc.cursor()
    cur.execute(str_query)
    for c in cur:
        if c[0]> 0 :
            res = True
    return res

def is_valid_housenumber(hsnr):
    is_valid = True
    if len(hsnr.encode('utf8')) > 11:
        is_valid = False
    return is_valid

def is_valid_fantoir(f):
    res = True
    if len(f) != 10:
        res = False
    return res

def load_hsnr_from_cad_file_csv(fnadresses,source):
    csvadresses = open(fnadresses,'r')
    dict_node_relations = {}
    for l in csvadresses :
        line_split = l.split(';')
        cle_interop,housenumber,pseudo_adresse,name,code_postal,lon,lat = line_split[0],line_split[2]+line_split[3],line_split[4],line_split[5],line_split[7],line_split[13],line_split[14]

        if len(name) < 2:
            continue
        if len(lon) < 1:
            continue
        if pseudo_adresse == 'true':
            # print(l)
            continue
        adresses.register(name)
        adresses.add_voie(name,'CADASTRE')
        if not cle_interop in dict_node_relations:
            dict_node_relations[cle_interop] = []
            dict_node_relations[cle_interop].append(normalize(name))
        if is_valid_housenumber(housenumber):
            nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
            adresses.add_adresse(Adresse(nd,housenumber,name,'',code_postal),source)

def load_hsnr_bbox_from_pg_osm(insee_com):
    data = get_data_from_pg('hsnr_bbox_insee',insee_com)
    for l in data:
        oa = Pg_hsnr(l)
        n = Node({'id':oa.osm_id,'lon':oa.x,'lat':oa.y},{})
        if oa.voie == None:
            continue
        if oa.fantoir == '':
            continue
        adresses.register(oa.voie)
        adresses.add_adresse(Adresse(n,oa.numero,oa.voie,oa.fantoir,oa.code_postal),source)

def load_hsnr_from_pg_osm(insee_com):
    data = get_data_from_pg('hsnr_insee',insee_com)
    for l in data:
        oa = Pg_hsnr(l)
        n = Node({'id':oa.osm_id,'lon':oa.x,'lat':oa.y},{})
        if oa.voie == None:
            continue
        adresses.register(oa.voie)
        adresses.add_adresse(Adresse(n,oa.numero,oa.voie,oa.fantoir,oa.code_postal),source)

def load_highways_bbox_from_pg_osm(insee_com):
    if commune_avec_suffixe:
        data = get_data_from_pg('highway_suffixe_insee',insee_com,False,geom_suffixe)
    else:
        data = get_data_from_pg('highway_bbox_insee',insee_com)
    for l in data:
        fantoir = ''
        if len(l)>1:
            if l[1] != None and l[1][0:5] == insee_com:
                fantoir = l[1]
        if len(l)>2 and fantoir == '':
            if l[2] != None and l[2][0:5] == insee_com:
                fantoir = l[2]
        if len(l)>3 and fantoir == '':
            if l[3] != None and l[3][0:5] == insee_com:
                fantoir = l[3]
        if fantoir == '':
            continue
        name = l[0]
        suffixe = ''
        if l[4]:
            suffixe = l[4]
        if len(name) < 2:
            continue
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        adresses.add_fantoir(cle,fantoir,'OSM')
        adresses.add_voie(name_suffixe,'OSM',name)

def load_highways_from_pg_osm(insee_com):
    if commune_avec_suffixe:
        data = get_data_from_pg('highway_suffixe_insee',insee_com,False,geom_suffixe)
    else:
        data = get_data_from_pg('highway_insee',insee_com)
    for l in data:
        name = l[0]
        suffixe = ''
        if l[4]:
            suffixe = l[4]
        if len(name) < 2:
            continue
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        fantoir = ''
        if len(l)>1:
            if l[1] != None and l[1][0:5] == insee_com:
                fantoir = l[1]
        if len(l)>2 and fantoir == '':
            if l[2] != None and l[2][0:5] == insee_com:
                fantoir = l[2]
        if len(l)>3 and fantoir == '':
            if l[3] != None and l[3][0:5] == insee_com:
                fantoir = l[3]
        if fantoir != '':
            adresses.add_fantoir(cle,fantoir,'OSM')
            dicts.add_fantoir_name(fantoir,name,'OSM')
        adresses.add_voie(name_suffixe,'OSM',name)

def load_highways_relations_bbox_from_pg_osm(insee_com):
    if commune_avec_suffixe:
        data = get_data_from_pg('highway_relation_suffixe_insee',insee_com,False,geom_suffixe)
    else:
        data = get_data_from_pg('highway_relation_bbox_insee',insee_com)
    for l in data:
        fantoir = ''
        tags = tags_list_as_dict(l[1])
        if 'ref:FR:FANTOIR' in tags:
            if tags['ref:FR:FANTOIR'][0:5] == code_insee and len(tags['ref:FR:FANTOIR']) == 10:
                fantoir = tags['ref:FR:FANTOIR']
        if fantoir == '':
            continue
        name = l[0]
        if len(name) < 2:
            continue
        suffixe = ''
        if commune_avec_suffixe and l[-2]:
            suffixe = l[-2]
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        adresses.add_voie(name_suffixe,'OSM',name)

def load_highways_relations_from_pg_osm(insee_com):
    if commune_avec_suffixe:
        data = get_data_from_pg('highway_relation_suffixe_insee',insee_com,False,geom_suffixe)
    else:
        data = get_data_from_pg('highway_relation_insee',insee_com)
    for l in data:
        name = l[0]
        if len(name) < 2:
            continue
        suffixe = ''
        if commune_avec_suffixe and l[-2]:
            suffixe = l[-2]
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        fantoir = ''
        tags = tags_list_as_dict(l[1])
        if 'ref:FR:FANTOIR' in tags:
            if tags['ref:FR:FANTOIR'][0:5] == code_insee and len(tags['ref:FR:FANTOIR']) == 10:
                fantoir = tags['ref:FR:FANTOIR']
        if fantoir != '':
            dicts.add_fantoir_name(fantoir,name,'OSM')
        adresses.add_voie(name_suffixe,'OSM',name)

def load_point_par_rue_from_pg_osm(insee_com):
    data = get_data_from_pg('point_par_rue_insee',insee_com)
    for l in data:
        name = l[2]
        if len(name) < 2:
            continue
        adresses.register(name)
        cle = normalize(name)
        adresses.a[cle]['point_par_rue'] = l[0:2]
        if 'OSM' not in adresses.a[cle]['voies']:
            adresses.add_voie(name,'OSM')
        if 'OSM' not in adresses.a[cle]['fantoirs']:
            if cle in dicts.fantoir:
                adresses.add_fantoir(cle,dicts.fantoir[cle],'OSM')

def load_point_par_rue_complement_from_pg_osm(insee_com):
    data = get_data_from_pg('point_par_rue_complement_insee',insee_com)
    for l in data:
        name = l[2]
        if len(name) < 2:
            continue
        fantoir = l[3]
        if fantoir and fantoir[0:5] != insee_com:
            continue
        if fantoir and len(fantoir) != 10:
            continue
        adresses.register(name)
        cle = normalize(name)
        adresses.a[cle]['point_par_rue'] = l[0:2]
        if fantoir:
            adresses.add_fantoir(cle,fantoir,'OSM')

def load_to_db(adresses,code_insee,source,code_dept):
    for a in ['cumul_adresses','cumul_voies']:
        sload = "DELETE FROM {:s} WHERE insee_com = '{:s}' AND source = '{:s}';\n".format(a,code_insee,source)
        cur_insert = pgc.cursor()
        cur_insert.execute(sload)
    nb_rec = 0
    a_values_voie = []

    for v in adresses.a:
        sload = 'INSERT INTO cumul_adresses (geometrie,numero,voie_cadastre,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source) VALUES'
        a_values = []
        street_name_cadastre = ''
        street_name_osm = ''
        street_name_fantoir = ''
        code_postal = ''
        cle_fantoir = get_best_fantoir(v)
        if 'OSM' in adresses.a[v]['voies']:
            street_name_osm =  adresses.a[v]['voies']['OSM']
        else :
            street_name_osm = dicts.get_fantoir_name(cle_fantoir,'OSM')
        if 'FANTOIR' in adresses.a[v]['voies']:
            street_name_fantoir =  adresses.a[v]['voies']['FANTOIR']
        if 'CADASTRE' in adresses.a[v]['voies']:
            street_name_cadastre =  adresses.a[v]['voies']['CADASTRE']
        if len(adresses.a[v]['point_par_rue'])>1 and source == 'OSM':
            a_values_voie.append(("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}',{:d})".format(adresses.a[v]['point_par_rue'][0],adresses.a[v]['point_par_rue'][1],street_name_cadastre.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,code_insee,code_dept,'',source,adresses.a[v]['highway_index'])).replace(",'',",",null,"))

        for num in adresses.a[v]['numeros']:
            numadresse = adresses.a[v]['numeros'][num]
            a_values.append("(ST_PointFromText('POINT({:s} {:s})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}')".format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.replace("'",""),street_name_cadastre.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,code_insee,code_dept,numadresse.code_postal,source).replace(",''",",null").replace(",''",",null"))
            nb_rec +=1
        if len(a_values)>0:
            sload = sload+','.join(a_values)+';COMMIT;'
            cur_insert.execute(sload)
    sload_voie = 'INSERT INTO cumul_voies (geometrie,voie_cadastre,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source,voie_index) VALUES'
    if len(a_values_voie) > 0:
        sload_voie = sload_voie+','.join(a_values_voie)+';COMMIT;'
        cur_insert.execute(sload_voie)
    return(nb_rec)

def load_type_highway_from_pg_osm(insee_com):
    data = get_data_from_pg('type_highway_insee',insee_com)
    for l in data:
        name = l[0]
        adresses.register(name)
        cle = normalize(name)
        if l[1] in dicts.highway_types:
            adresses.add_highway_index(cle,dicts.highway_types[l[1]])

def normalize(s):
    s = s.upper()                # tout en majuscules
    s = s.split(' (')[0]        # parenthèses : on coupe avant
    s = s.replace('-',' ')        # separateur espace
    s = s.replace('\'',' ')        # separateur espace
    s = s.replace('’',' ')        # separateur espace
    s = s.replace('/',' ')        # separateur espace
    s = s.replace(':',' ')        # separateur deux points
    s = ' '.join(s.split())        # separateur : 1 espace
    for l in iter(dicts.lettre_a_lettre):
        for ll in dicts.lettre_a_lettre[l]:
            s = s.replace(ll,l)

# type de voie
    abrev_trouvee = False
    p = 5
    while (not abrev_trouvee) and p > -1:
        p-= 1
        if get_part_debut(s,p) in dicts.abrev_type_voie:
            s = replace_type_voie(s,p)
            abrev_trouvee = True
# ordinal
    s = s.replace(' EME ','EME ')
    s = s.replace(' 1ERE',' PREMIERE')
    s = s.replace(' 1ER',' PREMIER')

# chiffres
    for c in dicts.chiffres:
        s = s.replace(c[0],c[1])

# titres, etc.
    for r in dicts.expand_noms:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])
    for r in dicts.expand_titres:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])
    for r in dicts.abrev_titres:
        s = s.replace(' '+r[0]+' ',' '+r[1]+' ')
        if s[-len(r[0]):] == r[0]:
            s = s.replace(' '+r[0],' '+r[1])

# articles
    for c in dicts.mot_a_blanc:
        s = s.replace(' '+c+' ',' ')

# chiffres romains
    sp = s.split()

    if len(sp)>0 and sp[-1] in dicts.chiffres_romains:
        sp[-1] = dicts.chiffres_romains[sp[-1]]
        s = ' '.join(sp)

# substitution complete
    if s in dicts.substitution_complete:
        s = dicts.substitution_complete[s]
    return s[0:30]

def replace_type_voie(s,nb):
    sp = s.split()
    spd = ' '.join(sp[0:nb])
    spf = ' '.join(sp[nb:len(sp)])
    s = dicts.abrev_type_voie[spd]+' '+spf
    return s

def tags_list_as_dict(ltags):
    res = {}
    for i in range(0,int(len(ltags)/2)):
        res[ltags[i*2]] = ltags[i*2+1]
    return res

def main(args):
    global source,batch_id
    global pgc,pgcl
    global code_insee,code_cadastre,code_dept
    global dicts
    global nodes,ways,adresses
    global commune_avec_suffixe
    global geom_suffixe
    global use_cache
    global schema_cible

    schema_cible = 'public'
    if ('SCHEMA_CIBLE' in os.environ) : schema_cible = (os.environ['SCHEMA_CIBLE'])

    use_cache = True

    debut_total = time.time()
    usage = 'USAGE : python addr_cad_2_db.py <code INSEE> <OSM|CADASTRE> {use_cache=True}'
    if len(args) < 3:
        print(usage)
        os._exit(0)
    if len(args) > 3:
        use_cache = args[3]
    source = args[2].upper()
    if source not in ['OSM','CADASTRE']:
        print(usage)
        os._exit(0)

    adresses = Adresses()

    pgc = get_pgc()
    pgcl = get_pgc_layers()

    code_insee = args[1]
    code_dept = get_short_code_dept_from_insee(code_insee)

    batch_id = batch_start_log(source,'loadCumul',code_insee)

    dicts = Dicts()
    dicts.load_all(code_insee)

    commune_avec_suffixe = has_addreses_with_suffix(code_insee)
    geom_suffixe = None
    if commune_avec_suffixe:
        geom_suffixe = get_geom_suffixes(code_insee)

    if source == 'CADASTRE':
        fnadresses = os.path.join(os.environ['BANO_CACHE_DIR'],code_dept,code_insee,'{}-bal.csv'.format(code_insee))
        load_hsnr_from_cad_file_csv(fnadresses,source)
    if source == 'OSM':
        load_hsnr_from_pg_osm(code_insee)
        load_hsnr_bbox_from_pg_osm(code_insee)
        load_type_highway_from_pg_osm(code_insee)
    load_highways_from_pg_osm(code_insee)
    load_highways_relations_from_pg_osm(code_insee)
    load_highways_bbox_from_pg_osm(code_insee)
    load_highways_relations_bbox_from_pg_osm(code_insee)
    add_fantoir_to_hsnr()
    load_point_par_rue_from_pg_osm(code_insee)
    load_point_par_rue_complement_from_pg_osm(code_insee)
    nb_rec = load_to_db(adresses,code_insee,source,code_dept)
    batch_end_log(nb_rec,batch_id)
    fin_total = time.time()

if __name__ == '__main__':
    main(sys.argv)

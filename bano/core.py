#!/usr/bin/env python
# coding: UTF-8

import os,os.path
import re
import sys
import time
import xml.etree.ElementTree as ET

from . import constants, db
from . import helpers as hp
from .models import Adresse, Adresses, Node, Pg_hsnr
from .outils_de_gestion import batch_start_log
from .outils_de_gestion import batch_end_log
from .outils_de_gestion import age_etape_dept
from .sources import fantoir

os.umask(0000)


def add_fantoir_to_hsnr():
    for v in adresses:
        if v in fantoir.mapping.fantoir:
            adresses[v]['fantoirs']['FANTOIR'] = fantoir.mapping.fantoir[v]
            adresses[v]['voies']['FANTOIR'] = fantoir.mapping.code_fantoir_vers_nom_fantoir[fantoir.mapping.fantoir[v]]
        else:
            if 'OSM' in adresses[v]['fantoirs']:
                if adresses[v]['fantoirs']['OSM'] in fantoir.mapping.code_fantoir_vers_nom_fantoir:
                    adresses[v]['voies']['FANTOIR'] = fantoir.mapping.code_fantoir_vers_nom_fantoir[adresses[v]['fantoirs']['OSM']]

def append_suffixe(name,suffixe):
    res = name
    if suffixe:
        name_norm = hp.normalize(name)
        suffixe_norm = hp.normalize(suffixe)
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
    if 'FANTOIR' in adresses[cle]['fantoirs']:
        res = adresses[cle]['fantoirs']['FANTOIR']
    if 'OSM' in adresses[cle]['fantoirs']:
        res = adresses[cle]['fantoirs']['OSM']
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
    cur = db.bano.cursor()
    cur.execute(str_query)
    for c in cur:
        code_cadastre = c[0]
    cur.close()
    return code_cadastre

def get_data_from_pg(data_type,insee_com,local=False,suffixe_data=None):
    cache_file = get_cache_filename(data_type,insee_com)
    if not use_cache or not os.path.exists(cache_file) or (time.time() - os.path.getmtime(cache_file)) > 86400 :
        fq = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(data_type)),'r')
        str_query = fq.read().replace('__com__',insee_com)
        fq.close()
        if local:
            conn = db.bano
        else:
            conn = db.bano_cache
        if suffixe_data:
            str_query = str_query.replace('__suffixe_data__',suffixe_data)
        cur = conn.cursor()
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

def get_last_base_update(query_name,insee_com):
    resp = 0
    str_query = "SELECT timestamp_maj FROM {} WHERE insee_com = '{}' LIMIT 1;".format(query_name,insee_com)
    cur = db.bano.cursor()
    cur.execute(str_query)
    for l in cur :
        resp = l[0]
    if resp == 0 :
        etape_dept = 'cache_dept_'+query_name
        if age_etape_dept(etape_dept,get_short_code_dept_from_insee(insee_com))  < 3600 :
            resp = round(time.time())
    cur.close()
    return resp

def get_data_from_pg_direct(query_name,insee_com):
    current_time = round(time.time())
    cur_cache = db.bano_cache.cursor()
    if not use_cache :
        fq = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'sql/{:s}.sql'.format(query_name)),'r')
        str_query = fq.read().replace('__com__',insee_com)
        fq.close()
        # print(round(time.time()))
        # print(str_query)
        cur_cache.execute(str_query)
        # print(round(time.time()))
        list_output = list()
        for lt in cur_cache :
            list_values = list()
            for item in list(lt):
                if item == None:
                    list_values.append('null')
                elif  type(item) == str :
                    # list_values.append("'{}'".format(item.replace("'","''")))
                    list_values.append("'{}'".format(item.replace("'","''").replace('"','')))
                elif type(item) == list :
                    if (len(item)) > 0 :
                        # list_values.append("hstore(ARRAY{})".format(str([s.replace("'","''") for s in item])))
                        list_values.append("hstore(ARRAY{})".format(str([s.replace("'","''").replace('"','') for s in item])))
                    else :
                        list_values.append('null')
                else :
                    list_values.append(str(item))
            list_values.append(str(current_time))            # print(list_values)

            str_values = ','.join(list_values).replace('"',"'")
            list_output.append(str_values)
        str_query = "DELETE FROM {} WHERE insee_com = '{}';".format(query_name,insee_com)
        cur_cache.execute(str_query)
        if len(list_output) > 0 :
            str_query = "INSERT INTO {} VALUES ({});COMMIT;".format(query_name,'),('.join(list_output))
            # print(str_query)
            cur_cache.execute(str_query)

    str_query = "SELECT * FROM {} WHERE insee_com = '{}';".format(query_name,insee_com)
    cur_cache.execute(str_query)

    res = []
    for l in cur_cache :
        res.append(list(l))
    cur_cache.close()
    return res

# def get_geom_suffixes(insee):
#     data = get_data_from_pg('geom_suffixes_insee',insee,True)
#     a_queries = []
#     for l in data:
#         a_queries.append('SELECT ST_PolygonFromText(\'{:s}\',3857) as geom,\'{:s}\'::text suffixe'.format(l[0],l[1].replace('\'','\'\'')))
#     return ' UNION '.join(a_queries)


def get_tags(xmlo):
    dtags = {}
    for tg in xmlo.iter('tag'):
        dtags[tg.get('k')] = tg.get('v')
    return dtags

def has_addreses_with_suffix(insee):
    res = False
    str_query = 'SELECT count(*) FROM suffixe where insee_com = \'{:s}\';'.format(insee)
    cur = db.bano.cursor()
    cur.execute(str_query)
    for c in cur:
        if c[0]> 0 :
            res = True
    cur.close()
    return res


def is_valid_fantoir(f):
    res = True
    if len(f) != 10:
        res = False
    return res

def load_cadastre_hsnr(code_insee):
    dict_node_relations = {}
    destinations_principales_retenues = 'habitation commerce industrie tourisme'
    str_query = "SELECT * FROM bal_cadastre WHERE commune_code = '{}';".format(code_insee)
    cur = db.bano_cache.cursor()
    cur.execute(str_query)
    for lt in cur:
        line_split = list(lt)
        # cle_interop,housenumber,pseudo_adresse,name,code_postal,destination_principale,lon,lat = line_split[0],line_split[2]+(str(line_split[3]) if (line_split[3]) else ''),line_split[4],line_split[5],(line_split[7] if line_split[7] else ''),line_split[9],line_split[13],line_split[14]
        cle_interop,housenumber,pseudo_adresse,name,code_postal,destination_principale,lon,lat = line_split[0],line_split[2]+(' '+str(line_split[3]) if (line_split[3]) else ''),line_split[4],line_split[5],(line_split[7] if line_split[7] else ''),line_split[9],line_split[13],line_split[14]
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
        
        if not cle_interop in dict_node_relations:
            dict_node_relations[cle_interop] = []
            dict_node_relations[cle_interop].append(hp.normalize(name))
        if hp.is_valid_housenumber(housenumber):
            nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
            adresses.add_adresse(Adresse(nd,housenumber,name,'',code_postal), 'CADASTRE')
    cur.close()

def load_bases_adresses_locales_hsnr(code_insee):
    dict_node_relations = {}
    str_query = "SELECT * FROM bal_locales WHERE commune_code = '{}';".format(code_insee)
    cur = db.bano_cache.cursor()
    cur.execute(str_query)
    for lt in cur:
        line_split = list(lt)
        cle_interop,housenumber,name,lon,lat = line_split[0],line_split[5]+(' '+str(line_split[6]) if (line_split[6]) else ''),line_split[4],line_split[7],line_split[8]
        if len(name) < 2:
            continue
        if not lon :
            continue
        adresses.register(name)
        if not cle_interop in dict_node_relations:
            dict_node_relations[cle_interop] = []
            dict_node_relations[cle_interop].append(hp.normalize(name))
        if hp.is_valid_housenumber(housenumber):
            nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
            adresses.add_adresse(Adresse(nd,housenumber,name,'',''), 'BAL')
    cur.close()

def load_hsnr_bbox_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('hsnr_bbox_insee',insee_com)
    for l in data:
        oa = Pg_hsnr(l, insee_com)
        n = Node({'id':oa.osm_id,'lon':oa.x,'lat':oa.y},{})
        if oa.voie == None:
            continue
        if oa.fantoir == '':
            continue
        adresses.register(oa.voie)
        adresses.add_adresse(Adresse(n,oa.numero,oa.voie,oa.fantoir,oa.code_postal), 'OSM')

def load_hsnr_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('hsnr_insee',insee_com)
    for l in data:
        oa = Pg_hsnr(l, insee_com)
        n = Node({'id':oa.osm_id,'lon':oa.x,'lat':oa.y},{})
        if oa.voie == None:
            continue
        adresses.register(oa.voie)
        adresses.add_adresse(Adresse(n,oa.numero,oa.voie,oa.fantoir,oa.code_postal), 'OSM')

def load_highways_bbox_from_pg_osm(insee_com):
    # if commune_avec_suffixe:
    data = get_data_from_pg_direct('highway_suffixe_insee',insee_com)
    # else:
    #     data = get_data_from_pg_direct('highway_bbox_insee',insee_com)
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
        cle = hp.normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        adresses.add_fantoir(cle,fantoir,'OSM')

def load_highways_from_pg_osm(insee_com):
    # if commune_avec_suffixe:
    data = get_data_from_pg_direct('highway_suffixe_insee',insee_com)
    # else:
    #     data = get_data_from_pg_direct('highway_insee',insee_com)
    #     # print(data)
        # data = get_data_from_pg('highway_insee',insee_com)
        # print(data)
    for l in data:
        name = l[0]
        suffixe = ''
        if l[4]:
            suffixe = l[4]
        if len(name) < 2:
            continue
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = hp.normalize(name_suffixe)
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
            fantoir.mapping.add_fantoir_name(fantoir,name,'OSM')

def load_highways_relations_bbox_from_pg_osm(code_insee):
    # if commune_avec_suffixe:
    data = get_data_from_pg_direct('highway_relation_suffixe_insee', code_insee)
    # else:
    #     data = get_data_from_pg_direct('highway_relation_bbox_insee',insee_com)
    for l in data:
        fantoir = ''
        tags = hp.tags_list_as_dict(l[1])
        if 'ref:FR:FANTOIR' in tags:
            if tags['ref:FR:FANTOIR'][0:5] == code_insee and len(tags['ref:FR:FANTOIR']) == 10:
                fantoir = tags['ref:FR:FANTOIR']
        if fantoir == '':
            continue
        name = l[0]
        if len(name) < 2:
            continue
        suffixe = ''
        # if commune_avec_suffixe and l[-2]:
        if l[-2]:
            suffixe = l[-2]
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = hp.normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue

def load_highways_relations_from_pg_osm(code_insee):
    # if commune_avec_suffixe:
    data = get_data_from_pg_direct('highway_relation_suffixe_insee', code_insee)
    # else:
    #     data = get_data_from_pg_direct('highway_relation_insee',insee_com)
    for l in data:
        name = l[0]
        if len(name) < 2:
            continue
        suffixe = ''
        if l[-2]:
            suffixe = l[-2]
        name_suffixe = append_suffixe(name,suffixe)
        adresses.register(name_suffixe)
        cle = hp.normalize(name_suffixe)
        if adresses.has_already_fantoir(cle,'OSM'):
            continue
        fantoir = ''
        tags = hp.tags_list_as_dict(l[1])
        if 'ref:FR:FANTOIR' in tags:
            if tags['ref:FR:FANTOIR'][0:5] == code_insee and len(tags['ref:FR:FANTOIR']) == 10:
                fantoir = tags['ref:FR:FANTOIR']
        if fantoir != '':
            fantoir.mapping.add_fantoir_name(fantoir,name,'OSM')

def load_point_par_rue_from_pg_osm(code_insee):
    data = get_data_from_pg_direct('point_par_rue_insee',code_insee)
    for l in data:
        name = l[2]
        if len(name) < 2:
            continue
        adresses.register(name)
        cle = hp.normalize(name)
        adresses[cle]['point_par_rue'] = l[0:2]
        if 'OSM' not in adresses[cle]['fantoirs']:
            if cle in fantoir.mapping.fantoir:
                adresses.add_fantoir(cle,fantoir.mapping.fantoir[cle],'OSM')

def load_point_par_rue_complement_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('point_par_rue_complement_insee',insee_com)
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
        cle = hp.normalize(name)
        adresses[cle]['point_par_rue'] = l[0:2]
        if fantoir:
            adresses.add_fantoir(cle,fantoir,'OSM')

def load_to_db(adresses,code_insee,source,code_dept):
    cur_insert = db.bano.cursor()
    for a in ['cumul_adresses','cumul_voies']:
        sload = "DELETE FROM {:s} WHERE insee_com = '{:s}' AND source = '{:s}';\n".format(a,code_insee,source)
        cur_insert.execute(sload)
    nb_rec = 0
    a_values_voie = []

    for v in adresses:
        sload = 'INSERT INTO cumul_adresses (geometrie,numero,voie_cadastre,voie_bal,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source) VALUES'
        a_values = []
        street_name_cadastre = ''
        street_name_bal = ''
        street_name_osm = ''
        street_name_fantoir = ''
        code_postal = ''
        cle_fantoir = get_best_fantoir(v)
        if 'OSM' in adresses[v]['voies']:
            street_name_osm =  adresses[v]['voies']['OSM']
        else :
            street_name_osm = fantoir.mapping.get_fantoir_name(cle_fantoir,'OSM')
        if 'FANTOIR' in adresses[v]['voies']:
            street_name_fantoir =  adresses[v]['voies']['FANTOIR']
        if 'CADASTRE' in adresses[v]['voies']:
            street_name_cadastre =  adresses[v]['voies']['CADASTRE']
        if 'BAL' in adresses[v]['voies']:
            street_name_bal =  adresses[v]['voies']['BAL']
        if len(adresses[v]['point_par_rue'])>1 and source == 'OSM':
            a_values_voie.append(("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}',{:d})".format(adresses[v]['point_par_rue'][0],adresses[v]['point_par_rue'][1],street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,code_insee,code_dept,'',source,adresses[v]['highway_index'])).replace(",'',",",null,"))

        for num in adresses[v]['numeros']:
            numadresse = adresses[v]['numeros'][num]
            a_values.append("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}')".format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.replace("'",""),street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,code_insee,code_dept,numadresse.code_postal,source).replace(",''",",null").replace(",''",",null"))
            nb_rec +=1
        if len(a_values)>0:
            sload = sload+','.join(a_values)+';COMMIT;'
            cur_insert.execute(sload)
    sload_voie = 'INSERT INTO cumul_voies (geometrie,voie_cadastre,voie_bal,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source,voie_index) VALUES'
    if len(a_values_voie) > 0:
        sload_voie = sload_voie+','.join(a_values_voie)+';COMMIT;'
        cur_insert.execute(sload_voie)
    cur_insert.close()
    return(nb_rec)

def load_type_highway_from_pg_osm(insee_com):
    data = get_data_from_pg_direct('type_highway_insee',insee_com)
    # import ipdb; ipdb.set_trace()
    for name, highway_type, *_ in data:
        adresses.register(name)
        cle = hp.normalize(name)
        if highway_type in constants.HIGHWAY_TYPES_INDEX:
            adresses.add_highway_index(cle,constants.HIGHWAY_TYPES_INDEX[highway_type])


# def hp.tags_list_as_dict(ltags):
#     res = {}
#     if (ltags):
#         # print(ltags)
#         ltags = ltags.replace('"=>"','","')
#         ltags = ltags.split(',')
#         # print(ltags)
#         for i in range(0,int(len(ltags)/2)):
#             res[ltags[i*2]] = ltags[i*2+1]
#     # print(res)
#     return res

def addr_2_db(code_insee, source, **kwargs):
    global batch_id
    global code_cadastre,code_dept
    global nodes,ways,adresses
    global geom_suffixe
    global use_cache
    global schema_cible

    schema_cible = 'public'
    if ('SCHEMA_CIBLE' in os.environ) : schema_cible = (os.environ['SCHEMA_CIBLE'])

    use_cache = False

    debut_total = time.time()
    usage = 'USAGE : python addr_cad_2_db.py <code INSEE> <OSM|CADASTRE|BAL> {use_cache=True}'
    
    adresses = Adresses()

    fantoir.mapping.load_all(code_insee)

    code_dept = get_short_code_dept_from_insee(code_insee)

    batch_id = batch_start_log(source,'loadCumul',code_insee)

    # commune_avec_suffixe = has_addreses_with_suffix(code_insee)
    # geom_suffixe = None
    # if commune_avec_suffixe:
    #     geom_suffixe = get_geom_suffixes(code_insee)
    if source == 'BAL':
        load_bases_adresses_locales_hsnr(code_insee)
    if source == 'CADASTRE':
        load_cadastre_hsnr(code_insee)
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

import re

from . import db
from . import helpers as hp
from .sources import fantoir


class Adresse:
    def __init__(self, node, num, voie, fantoir, code_postal):
        self.node = node
        self.numero = num
        self.voie = voie
        self.fantoir = fantoir
        self.code_postal = code_postal


class Adresses:
    def __init__(self, code_insee):
        self.a = {}
        self.code_insee = code_insee

    def __contains__(self, item):
        return item in self.a

    def __getitem__(self, key):
        return self.a[key]

    def __setitem__(self, key, value):
        self.a[key] = value

    def __iter__(self):
        return iter(self.a)

    def register(self, voie):
        cle = hp.normalize(voie)
        if not cle in self:
            self[cle] = {'numeros':{},'voies':{},'fantoirs':{},'point_par_rue':[],'highway_index':0}

    def add_fantoir(self,cle,fantoir,source):
        self.register(cle)
        if len(fantoir) == 10:
            self[cle]['fantoirs'][source] = fantoir

    def add_voie(self,voie_cle,source,voie=None):
        cle = hp.normalize(voie_cle)
        self[cle]['voies'][source] = voie or voie_cle

    def add_adresse(self,ad,source):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        if (ad.fantoir == '' or hp.is_valid_fantoir(ad.fantoir, self.code_insee)) and hp.is_valid_housenumber(ad.numero):
            cle = hp.normalize(ad.voie)
            self.add_voie(ad.voie,source)
            self[cle]['numeros'][ad.numero] = ad
            if ad.fantoir != '':
                self[cle]['fantoirs']['OSM'] = ad.fantoir

    def get_cle_by_fantoir(self,fantoir):
        cle = ''
        for c in self:
            if 'fantoirs' in self[c]:
                if 'OSM' in self[c]['fantoirs']:
                    if self[c]['fantoirs']['OSM'] == fantoir:
                        cle = c
                        break
                if 'FANTOIR' in self[c]['fantoirs']:
                    if self[c]['fantoirs']['FANTOIR'] == fantoir:
                        cle = c
                        break
        return cle

    def get_best_fantoir(self, cle):
        return self[cle]['fantoirs'].get('FANTOIR') or self[cle]['fantoirs'].get('OSM') or ''

    def has_already_fantoir(self,cle,source):
        return source in self[cle]['fantoirs']

    def add_highway_index(self,cle,val):
        self[cle]['highway_index']+=val

    def load_cadastre_hsnr(self):
        dict_node_relations = {}
        destinations_principales_retenues = 'habitation commerce industrie tourisme'
        str_query = "SELECT * FROM bal_cadastre WHERE commune_code = '{}';".format(self.code_insee)
        cur = db.bano_cache.cursor()
        cur.execute(str_query)
        for cle_interop, ui_adresse, numero, suffixe, pseudo_adresse, name, voie_code, code_postal, libelle_acheminement, destination_principale, commune_code, commune_nom, source, lon, lat, *others in cur:
            housenumber = numero+((' '+suffixe) if suffixe else '')
            if not name or len(name) < 2:
                continue
            if not lon :
                continue
            if pseudo_adresse == 'true':
                continue
            if not re.search(destination_principale,destinations_principales_retenues):
                continue
            self.register(name)
            
            if not cle_interop in dict_node_relations:
                dict_node_relations[cle_interop] = []
                dict_node_relations[cle_interop].append(hp.normalize(name))
            if hp.is_valid_housenumber(housenumber):
                nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
                self.add_adresse(Adresse(nd,housenumber,name,'',code_postal), 'CADASTRE')
        cur.close()

    def save(self, source, code_dept):
        cur_insert = db.bano.cursor()
        for a in ['cumul_adresses','cumul_voies']:
            sload = "DELETE FROM {:s} WHERE insee_com = '{:s}' AND source = '{:s}';\n".format(a, self.code_insee, source)
            cur_insert.execute(sload)
        nb_rec = 0
        a_values_voie = []

        for v in self:
            sload = 'INSERT INTO cumul_adresses (geometrie,numero,voie_cadastre,voie_bal,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source) VALUES'
            a_values = []
            street_name_cadastre = ''
            street_name_bal = ''
            street_name_osm = ''
            street_name_fantoir = ''
            code_postal = ''
            cle_fantoir = self.get_best_fantoir(v)
            if 'OSM' in self[v]['voies']:
                street_name_osm =  self[v]['voies']['OSM']
            else :
                street_name_osm = fantoir.mapping.get_fantoir_name(cle_fantoir,'OSM')
            if 'FANTOIR' in self[v]['voies']:
                street_name_fantoir =  self[v]['voies']['FANTOIR']
            if 'CADASTRE' in self[v]['voies']:
                street_name_cadastre =  self[v]['voies']['CADASTRE']
            if 'BAL' in self[v]['voies']:
                street_name_bal =  self[v]['voies']['BAL']
            if len(self[v]['point_par_rue'])>1 and source == 'OSM':
                a_values_voie.append(("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}',{:d})".format(self[v]['point_par_rue'][0],self[v]['point_par_rue'][1],street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"), street_name_fantoir.replace("'","''"), cle_fantoir, self.code_insee,code_dept,'',source,self[v]['highway_index'])).replace(",'',",",null,"))

            for num in self[v]['numeros']:
                numadresse = self[v]['numeros'][num]
                a_values.append("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}')".format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.replace("'",""),street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,self.code_insee,code_dept,numadresse.code_postal,source).replace(",''",",null").replace(",''",",null"))
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


class Pg_hsnr:
    def __init__(self, d, code_insee):
        self.x, self.y, self.provenance, self.osm_id, self.numero, self.voie, self.tags, *others = d
        self.tags = self.tags or {} 
        self.fantoir = ''
        if self.provenance == '3' or self.provenance == '4':
            self.set_street_name()
        self.set_fantoir(code_insee)
        self.code_postal = hp.find_cp_in_tags(self.tags)

    def set_street_name(self):
        if 'type' in self.tags and self.tags['type'] == 'associatedStreet' and 'name' in self.tags:
            self.voie = self.tags['name']

    def set_fantoir(self, code_insee):
        if 'ref:FR:FANTOIR' in self.tags and len(self.tags['ref:FR:FANTOIR']) == 10 and self.tags['ref:FR:FANTOIR'][0:5] == code_insee:
            self.fantoir = self.tags['ref:FR:FANTOIR']

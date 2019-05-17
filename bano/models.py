from . import helpers as hp


class Adresse:
    def __init__(self, node, num, voie, fantoir, code_postal):
        self.node = node
        self.numero = num
        self.voie = voie
        self.fantoir = fantoir
        self.code_postal = code_postal


class Adresses:
    def __init__(self):
        self.a = {}

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
        if not voie:
            voie = voie_cle
        self[cle]['voies'][source] = voie

    def add_adresse(self,ad,source):
        """ une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        if (ad.fantoir == '' or (is_valid_fantoir(ad.fantoir) and ad.fantoir[0:5] == code_insee)) and hp.is_valid_housenumber(ad.numero):
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

    def has_already_fantoir(self,cle,source):
        return source in self[cle]['fantoirs']

    def add_highway_index(self,cle,val):
        self[cle]['highway_index']+=val


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
        self.x = d[0]
        self.y = d[1]
        self.provenance = d[2]
        self.osm_id = d[3]
        self.numero = d[4]
        self.voie = d[5]
        self.tags = hp.tags_list_as_dict(d[6])
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

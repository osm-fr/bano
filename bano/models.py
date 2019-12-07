import re
import time

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
                self[cle]['fantoirs'][source] = ad.fantoir

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
        str_query = f"SELECT * FROM bal_cadastre WHERE commune_code = '{self.code_insee}' AND destination_principale in ('habitation','commerce','industrie','tourisme');"
        with db.bano_cache.cursor() as cur:
            cur.execute(str_query)
            for cle_interop, ui_adresse, numero, suffixe, pseudo_adresse, name, voie_code, code_postal, libelle_acheminement, destination_principale, commune_code, commune_nom, source, lon, lat, *others in cur:
                housenumber = numero+((' '+suffixe) if suffixe and suffixe.isalnum() else '')
                if not name or len(name) < 2 or not lon or pseudo_adresse == 'true':
                    continue
                self.register(name)
                
                if not cle_interop in dict_node_relations:
                    dict_node_relations[cle_interop] = []
                    dict_node_relations[cle_interop].append(hp.normalize(name))
                if hp.is_valid_housenumber(housenumber):
                    nd = Node({'id':cle_interop,'lon':lon,'lat':lat},{})
                    self.add_adresse(Adresse(nd,housenumber,name,'',code_postal), 'CADASTRE')

    def save(self, source, code_dept):
        with db.bano.cursor() as cur_insert :
            for a in ['cumul_adresses','cumul_voies']:
                cur_insert.execute(f"DELETE FROM {a} WHERE insee_com = '{self.code_insee}' AND source = '{source}';")
            nb_rec = 0
            a_values = []
            a_values_voie = []
            sload = 'INSERT INTO cumul_adresses (geometrie,numero,voie_cadastre,voie_bal,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source) VALUES'
            for v in self:
                code_postal = ''
                cle_fantoir = self.get_best_fantoir(v)
                street_name_osm = self[v]['voies'].get('OSM') or fantoir.mapping.get_fantoir_name(cle_fantoir,'OSM') or ''
                street_name_fantoir =  self[v]['voies'].get('FANTOIR') or ''
                street_name_cadastre =  self[v]['voies'].get('CADASTRE') or ''
                street_name_bal =  self[v]['voies'].get('BAL') or ''

                if len(self[v]['point_par_rue'])>1 and source == 'OSM':
                    a_values_voie.append(("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}',{:d})".format(self[v]['point_par_rue'][0],self[v]['point_par_rue'][1],street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"), street_name_fantoir.replace("'","''"), cle_fantoir, self.code_insee,code_dept,'',source,self[v]['highway_index'])).replace(",'',",",null,"))

                for num in self[v]['numeros']:
                    numadresse = self[v]['numeros'][num]
                    a_values.append("(ST_PointFromText('POINT({:6f} {:6f})', 4326),'{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}','{:s}')".format(numadresse.node.attribs['lon'],numadresse.node.attribs['lat'],numadresse.numero.replace("'",""),street_name_cadastre.replace("'","''"),street_name_bal.replace("'","''"),street_name_osm.replace("'","''"),street_name_fantoir.replace("'","''"),cle_fantoir,self.code_insee,code_dept,numadresse.code_postal,source).replace(",''",",null").replace(",''",",null"))
                    nb_rec +=1
            if len(a_values)>0:
                cur_insert.execute(sload+','.join(a_values)+';COMMIT;')
            sload_voie = 'INSERT INTO cumul_voies (geometrie,voie_cadastre,voie_bal,voie_osm,voie_fantoir,fantoir,insee_com,dept,code_postal,source,voie_index) VALUES'
            if len(a_values_voie) > 0:
                sload_voie = sload_voie+','.join(a_values_voie)+';COMMIT;'
                cur_insert.execute(sload_voie)
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
        if self.provenance == 3 or self.provenance == 4:
            self.set_street_name()
        self.set_fantoir(code_insee)
        self.code_postal = hp.find_cp_in_tags(self.tags)

    def set_street_name(self):
        if 'type' in self.tags and self.tags['type'] == 'associatedStreet' and 'name' in self.tags:
            self.voie = self.tags['name']

    def set_fantoir(self, code_insee):
        if 'ref:FR:FANTOIR' in self.tags and len(self.tags['ref:FR:FANTOIR']) == 10 and self.tags['ref:FR:FANTOIR'][0:5] == code_insee:
            self.fantoir = self.tags['ref:FR:FANTOIR']

class Fantoir:
    def __init__(self,name,fantoir,bati):
        self.name = name
        self.name_norm = hp.normalize(name)
        self.fantoir = fantoir
        self.bati = bati
class Cadastre:
    def __init__(self,lon,lat,name):
        self.lon = lon
        self.lat = lat
        self.name = name
        self.name_norm = hp.normalize(name)
class Osm:
    def __init__(self,lon,lat,place,name,fantoir):
        self.lon = lon
        self.lat = lat
        self.place = place
        self.name = name
        self.name_norm = hp.normalize(name)
        self.fantoir = fantoir
class Place:
    def __init__(self,lon,lat,place,name_fantoir,name_cadastre,name_osm,fantoir,bati,code_insee):
        self.has_fantoir = False
        self.has_osm = False
        self.has_cadastre = False
        self.fantoir = Fantoir(name_fantoir,fantoir,bati)
        self.osm = Osm(lon,lat,place,name_osm,fantoir)
        self.cadastre = Cadastre(lon,lat,name_cadastre)
        self.code_insee = str(code_insee)
        self.code_dept = hp.get_code_dept_from_insee(self.code_insee)
        if self.fantoir.name != '':
            self.has_fantoir = True
        if self.osm.name != '':
            self.has_osm = True
        if self.cadastre.name != '':
            self.has_cadastre = True
        self.id = self.fantoir.fantoir or (self.cadastre.name_norm or self.osm.name_norm)
    def update_fantoir(self,name,fantoir,bati):
        self.fantoir = Fantoir(name,fantoir,bati)
        self.has_fantoir = True
    def update_osm(self,lon,lat,place,name,fantoir=''):
        self.osm = Osm(lon,lat,place,name,fantoir)
        self.has_osm = True
    def update_cadastre(self,lon,lat,name):
        self.cadastre = Cadastre(lon,lat,name)
        self.has_cadastre = True
    def as_string(self):
        return "{:s}:{:s}\t{:s}\t{:6f}\t{:6f}\t{:s}\t{:s}\t{:6f}\t{:6f}\t{:s}".format(self.id,self.fantoir.name,self.fantoir.fantoir,self.osm.lon,self.osm.lat,self.osm.place,self.osm.name,self.cadastre.lon,self.cadastre.lat,self.cadastre.name)
    def as_SQL_cadastre_row(self):
        if self.has_cadastre:
            return hp.remove_quotes_on_null(f"(ST_PointFromText('POINT({self.cadastre.lon} {self.cadastre.lat})',4326),'{hp.escape_quotes(hp.format_toponyme(self.cadastre.name)) or 'null'}','{hp.escape_quotes(self.osm.name) or 'null'}','{hp.escape_quotes(self.fantoir.name) or 'null'}','{self.fantoir.fantoir or 'null'}','{self.code_insee}','{self.code_dept}','null','CADASTRE',{self.fantoir.bati or 'null'},'')")
    def as_SQL_osm_row(self):
        return hp.remove_quotes_on_null(f"(ST_PointFromText('POINT({self.osm.lon} {self.osm.lat})',4326),null,'{hp.escape_quotes(self.osm.name) or 'null'}','{hp.escape_quotes(self.fantoir.name) or 'null'}','{self.fantoir.fantoir or 'null'}','{self.code_insee}','{self.code_dept}',null,'OSM',{self.fantoir.bati or 'null'},'{self.osm.place}')")

class Places:
    def __init__(self):
        self.p = {}

    def add_place(self,new_p):
        self.p[new_p.id]=new_p
    def match_fantoir(self,fantoir):
        for c in self.p:
            if c.fantoir and c.fantoir.fantoir and c.fantoir.fantoir == fantoir:
                return c
        return 0
    def match_name(self,name,target):
        res = []
        name_norm = hp.normalize(name)
        if target == 'FANTOIR':
            for c in self.p:
                if self.p[c].fantoir and self.p[c].fantoir.name and self.p[c].fantoir.name_norm == name_norm:
                    res+=[c]
        if target == 'CADASTRE':
            for c in self.p:
                if c.cadastre and c.cadastre.name and c.cadastre.name_norm == name_norm:
                    res+=c
        if target == 'OSM':
            for c in self.p:
                if c.osm and c.osm.name and c.osm.name_norm == name_norm:
                    res+=c
        return res
    def _print(self):
        for c in self.p:
            print(self.p[c].osm.name)
            print(self.p[c].as_string())
    def _print_SQL_Cadastre(self):
        for c in self.p:
            print(self.p[c].as_SQL_cadastre_row())
    def as_SQL_Cadastre_array(self):
        a = []
        for c in self.p:
            if self.p[c].has_cadastre:
                a.append(self.p[c].as_SQL_cadastre_row())
        return a
    def as_SQL_OSM_array(self):
        a = []
        for c in self.p:
            if self.p[c].has_osm:
                a.append(self.p[c].as_SQL_osm_row())
        return a


class Tile:
    def __init__(self,z,x,y):
        self.x = x
        self.y = y
        self.z = z
        self.xmin = -20037508.34 + (40075016.68/(2 ** self.z)) *  self.x
        self.xmax = -20037508.34 + (40075016.68/(2 ** self.z)) * (self.x + 1)
        self.ymin = 20037508.34 - (40075016.68/(2 ** self.z)) * (self.y + 1)
        self.ymax = 20037508.34 - (40075016.68/(2 ** self.z)) *  self.y

class Tiles:
    def __init__(self):
        self.t = {}

    def add_tile(self,z,x,y):
        self.t[f"{z}/{x}/{y}"] = Tile(z,x,y)

    def add_tiles_from_file(self,tilefile):
        with open(tilefile,'r') as f:
            for ligne in f.readlines():
                self.add_tile(int(ligne.split('/')[0]),int(ligne.split('/')[1]),int(ligne.split('/')[2]))

    def as_list_of_SQL_values(self):
        return [f"({self.t[tile].z},{self.t[tile].x},{self.t[tile].y},ST_SetSRID(ST_MakeBox2D(ST_Point({int(self.t[tile].xmin)},{int(self.t[tile].ymin)}),ST_Point({int(self.t[tile].xmax)},{int(self.t[tile].ymax)})),3857))" for tile in self.t]

    def convert_to_insee_list(self):
        with db.bano_cache.cursor() as cur:
            cur.execute("TRUNCATE TABLE expire_tiles;COMMIT;")
            SQL_values = self.as_list_of_SQL_values()
            while len(SQL_values) > 10000:
                cur.execute(f"""INSERT INTO expire_tiles VALUES {','.join(SQL_values[0:10000])};COMMIT; """)
                SQL_values = SQL_values[10000:]
            if SQL_values:
                cur.execute(f"""INSERT INTO expire_tiles VALUES {','.join(SQL_values)};COMMIT; """)
            cur.execute("""SELECT p."ref:INSEE"
                         FROM planet_osm_polygon p
                         JOIN expire_tiles e
                         ON ST_intersects(p.way, e.geometrie)
                         WHERE p.way && e.geometrie AND
                         p.admin_level = 8 AND
                         p.boundary = 'administrative' AND
                         p."ref:INSEE" NOT IN ('13055','69123','75056') AND
                         COALESCE(p."ref:INSEE",'') != ''
                         UNION
                         SELECT p."ref:INSEE"
                         FROM planet_osm_polygon p
                         JOIN expire_tiles e
                         ON ST_intersects(p.way, e.geometrie)
                         WHERE p.way && e.geometrie AND
                         p.admin_level = 9 AND
                         p.boundary = 'administrative' AND
                         (p."ref:INSEE" LIKE '132__' OR
                          p."ref:INSEE" LIKE '6938_' OR
                          p."ref:INSEE" LIKE '751__') 
                         ORDER BY 1;""")
            return [f[0]for f in cur]


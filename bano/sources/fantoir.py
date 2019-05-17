from bano import db

class Mapping:
    def __init__(self):
        self.fantoir = {}
        self.code_fantoir_vers_nom_fantoir = {}
        self.code_fantoir_vers_noms = {}

    def load_fantoir(self,insee):
        str_query = ("""SELECT *
                        FROM    (SELECT code_insee||id_voie||cle_rivoli,
                                        nature_voie||' '||libelle_voie,
                                        rank() OVER(PARTITION BY nature_voie||' '||libelle_voie ORDER BY type_voie,id_voie,cle_rivoli) rang
                                FROM    fantoir_voie
                                WHERE    code_insee = '%s' AND
                                        caractere_annul NOT IN ('O','Q')) a
                        WHERE rang = 1;""" % insee)
        cur_fantoir = db.bano_cache.cursor()
        cur_fantoir.execute(str_query)
        for c in cur_fantoir:
            self.code_fantoir_vers_nom_fantoir[c[0]] = c[1]
            cle = ' '.join(c[1].replace('-',' ').split())
            cle = normalize(cle)
            self.fantoir[cle] = c[0]
        cur_fantoir.close()

    def load_addr_from_fantoir(self):
        for k in self.fantoir:
            adresses.add_fantoir(k,self.fantoir[k],'FANTOIR')

    def load_all(self,code_insee_commune):
        self.load_fantoir(code_insee_commune)

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


mapping = Mapping()

from bano import db
from ..helpers import normalize

class Mapping:
    def __init__(self):
        self.fantoir = {}
        self.code_fantoir_vers_nom_fantoir = {}
        self.code_fantoir_vers_noms = {}

    def reset(self):
        self.fantoir = {}
        self.code_fantoir_vers_nom_fantoir = {}
        self.code_fantoir_vers_noms = {}

    def load(self,insee):
        str_query = ("""SELECT *
                        FROM    (SELECT code_insee||id_voie||cle_rivoli,
                                        nature_voie||' '||libelle_voie,
                                        rank() OVER(PARTITION BY nature_voie||' '||libelle_voie ORDER BY type_voie,id_voie,cle_rivoli) rang
                                FROM    fantoir_voie
                                WHERE    code_insee = '%s' AND
                                        caractere_annul NOT IN ('O','Q')) a
                        WHERE rang = 1;""" % insee)
        with db.bano_cache.cursor() as cur_fantoir:
            cur_fantoir.execute(str_query)
            for c in cur_fantoir:
                self.code_fantoir_vers_nom_fantoir[c[0]] = c[1]
                cle = ' '.join(c[1].replace('-',' ').split())
                cle = normalize(cle)
                self.fantoir[cle] = c[0]

    def load_lieux_dits(self,insee):
        str_query = "SELECT code_insee||id_voie||cle_rivoli,\
                            TRIM(BOTH FROM nature_voie||' '||libelle_voie),\
                            ld_bati\
                    FROM    fantoir_voie\
                    WHERE    code_insee = '{:s}' AND\
                            type_voie = '3' AND\
                            COALESCE(caractere_annul,'') = '';".format(insee)
        with db.bano_cache.cursor() as conn:
            conn.execute(str_query)
            for c in conn:
                self.fantoir[c[0]] = {"nom":c[1], "ld_bati":c[2]}
    
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

#!/usr/bin/env python
# coding: UTF-8

import io
import json
from collections import defaultdict, OrderedDict

from .db import bano_db
from . import helpers as hp

# from .sources import fantoir
from .sql import sql_get_data, sql_process


class Nom:
    def __init__(
        self,
        nom,
        fantoir,
        nature,
        source,
        code_insee,
        code_insee_ancienne_commune,
        nom_ancienne_commune,
    ):
        self.code_insee = code_insee
        self.code_insee_ancienne_commune = code_insee_ancienne_commune
        self.nom = nom
        self.nom_ancienne_commune = nom_ancienne_commune
        self.fantoir = fantoir[0:9] if fantoir else None
        self.nature = nature
        self.source = source
        self.nom_normalise = hp.normalize(nom)

    def __eq__(self, other):
        return (
            self.nom == other.nom
            and self.fantoir == other.fantoir
            and self.nature == other.nature
            and self.source == other.source
            and self.code_insee == other.code_insee
            and self.code_insee_ancienne_commune == other.code_insee_ancienne_commune
        )

    def __hash__(self):
        return hash(
            (
                self.nom,
                self.fantoir,
                self.source,
                self.nature,
                self.code_insee,
                self.code_insee_ancienne_commune,
            )
        )

    def _as_csv_format_bano(self):
        return f"{self.fantoir}\t{self.nom}\t{self.nature}\t{self.code_insee}\t{self.code_insee_ancienne_commune if self.code_insee_ancienne_commune else ''}\t{self.nom_ancienne_commune if self.nom_ancienne_commune else ''}\t{self.source}"

    def add_fantoir(self, topo):
        if not self.fantoir:
            self.fantoir = topo.topo.get(self.nom_normalise)

class Noms:
    def __init__(self, code_insee):
        self.code_insee = code_insee
        self.triplets_nom_fantoir_source = []
        self.fantoir_par_nom_sous_commune = {"RACINE": defaultdict(list)}

    def __iter__(self):
        return iter(self.triplets_nom_fantoir_source)

    def _print(self, pattern=None):
        for a in self:
            if not pattern or pattern in a._as_csv_format_bano():
                print(a._as_csv_format_bano())

    # On ne charge pas les noms des numeros OSM. Ils sont ajoutés via Adresses.nom_des_adresses
    def charge_noms_osm_hors_numeros(self):
        data = (
            sql_get_data(
                "charge_noms_voies_lieux-dits_OSM",
                dict(code_insee=self.code_insee),
            )
            + sql_get_data(
                "charge_noms_voies_relation_bbox_OSM",
                dict(code_insee=self.code_insee),
            )
            + sql_get_data(
                "charge_noms_voies_relation_OSM",
                dict(code_insee=self.code_insee),
            )
        )
        for (
            provenance,
            name,
            tags,
            libelle_suffixe,
            code_insee_ancienne_commune,
            nom_ancienne_commune,
            nature,
        ) in data:
            if provenance in (1, 2, 3, 4, 5):
                self.add_nom(
                    Nom(
                        name,
                        tags.get("ref:FR:FANTOIR"),
                        nature,
                        "OSM",
                        self.code_insee,
                        code_insee_ancienne_commune,
                        nom_ancienne_commune,
                    )
                )
            if provenance in (6, 7) and tags.get("ref:FR:FANTOIR"):
                self.add_nom(
                    Nom(
                        name,
                        tags["ref:FR:FANTOIR"],
                        nature,
                        "OSM",
                        self.code_insee,
                        code_insee_ancienne_commune,
                        nom_ancienne_commune,
                    )
                )

    # On ajoute un triplet nom s'il n'a pas de FANTOIR ou si son FANTOIR appartient à la commune
    def add_nom(self, nom=Nom):
        if not nom.fantoir or nom.fantoir[0:5] == self.code_insee:
            self.triplets_nom_fantoir_source.append(nom)

    def add_fantoir(self, topo):
        for t in self.triplets_nom_fantoir_source:
            t.add_fantoir(topo)

    def remplit_fantoir_par_nom_sous_commune(self):
        for t in self.triplets_nom_fantoir_source:
            if t.code_insee_ancienne_commune:
                if (
                    not t.code_insee_ancienne_commune
                    in self.fantoir_par_nom_sous_commune
                ):
                    self.fantoir_par_nom_sous_commune[
                        t.code_insee_ancienne_commune
                    ] = {}
                self.fantoir_par_nom_sous_commune[t.code_insee_ancienne_commune][
                    t.nom
                ] = t.fantoir
            else:
                self.fantoir_par_nom_sous_commune[t.nom] = t.fantoir

    # def affiche_fantoir_par_nom_sous_commune(self):
    #     for branche,noms_fantoir in self.fantoir_par_nom_sous_commune.items():
    #         for nom,fantoir in noms_fantoir.items():
    #             print(f"{branche} - {nom} : {fantoir}")

    #         # print(f"{branche} - {nom}")
    #         # print(f"{branche} - {nom} > {self.fantoir_par_nom_sous_commune[branche][nom]}")

    def enregistre(self):
        sql_process(
            "suppression_noms_commune",
            dict(code_insee=self.code_insee),
        )
        io_in_csv = io.StringIO()
        for t in set(self.triplets_nom_fantoir_source):
            if t.fantoir:
                io_in_csv.write(t._as_csv_format_bano() + "\n")
        io_in_csv.seek(0)
        with bano_db.cursor() as cur_insert:
            cur_insert.copy_from(
                io_in_csv,
                "nom_fantoir",
                null="",
                columns=(
                    "fantoir",
                    "nom",
                    "nature",
                    "code_insee",
                    "code_insee_ancienne_commune",
                    "nom_ancienne_commune",
                    "source",
                ),
            )


class Adresse:
    def __init__(
        self,
        code_insee,
        x,
        y,
        num,
        source,
        voie=None,
        place=None,
        fantoir=None,
        code_postal=None,
        code_insee_ancienne_commune=None,
        nom_ancienne_commune=None,
    ):
        self.code_insee = code_insee
        self.x = round(x, 6)
        self.y = round(y, 6)
        self.source = source
        self.numero = num
        self.voie = voie
        self.place = place
        self.fantoir = fantoir[0:9] if fantoir else None
        self.code_postal = code_postal
        self.code_insee_ancienne_commune = code_insee_ancienne_commune
        self.nom_ancienne_commune = nom_ancienne_commune
        self.voie_normalisee = hp.normalize(self.voie) if self.voie else None
        self.place_normalisee = hp.format_toponyme(self.place) if self.place else None

    def __hash__(self):
        return hash(
            (
                self.code_insee,
                self.source,
                self.numero,
                self.voie,
                self.place,
                self.code_insee_ancienne_commune,
            )
        )

    def __eq__(self, other):
        return (
            self.code_insee == other.code_insee
            and self.source == other.source
            and self.numero == other.numero
            and self.voie == other.voie
            and self.place == other.place
            and self.code_insee_ancienne_commune == other.code_insee_ancienne_commune
        )

    def _as_csv_format_bano(self):
        return f"{self.fantoir if self.fantoir else ''}\t{self.x}\t{self.y}\t{self.numero}\t{self.voie if self.voie else ''}\t{self.place if self.place else ''}\t{self.code_postal}\t{self.code_insee}\t{self.code_insee_ancienne_commune if self.code_insee_ancienne_commune else ''}\t{self.nom_ancienne_commune if self.nom_ancienne_commune else ''}\t{self.source}"

    def _as_string(self):
        return f"source : {self.source}, numero : {self.numero}, voie : {self.voie} ({self.voie_normalisee}), place : {self.place}, fantoir : {self.fantoir}, code_postal:{self.code_postal}, sous_commune : {self.code_insee_ancienne_commune} - {self.nom_ancienne_commune}"


class Adresses:
    def __init__(self, code_insee):
        self.code_insee = code_insee
        self.liste = []
        self.index_voie = defaultdict(list)
        self.noms_de_voies = set()

    # def __contains__(self, item):
    #     return item in self.a

    def __getitem__(self, key):
        return self.liste[key]

    # def __setitem__(self, key, value):
    #     self.a[key] = value

    def __iter__(self):
        return iter(self.liste)

    def _print(self, pattern=None):
        for a in self:
            if not pattern or pattern in a._as_string():
                print(a._as_string())

    def add_adresse(self, ad):
        """une adresses est considérée dans la commune si sans Fantoir ou avec un Fantoir de la commune"""
        # if (ad.fantoir == None or hp.is_valid_fantoir(ad.fantoir, self.code_insee)) and hp.is_valid_housenumber(ad.numero):
        self.liste.append(ad)
        self.index_voie[ad.voie].append(len(self.liste) - 1)
        self.noms_de_voies.add(ad.voie)

    # def add_fantoir(self):
    #     for nom in self.noms:
    #         fantoir = topo.topo.get(a.voie_normalisee)

    def charge_numeros_ban(self, topo):
        data = sql_get_data("charge_ban_commune", dict(code_insee=self.code_insee))
        for (
            id_fantoir,
            numero,
            voie,
            lon,
            lat,
            code_postal,
            code_insee_ancienne_commune,
            nom_ancienne_commune,
        ) in data:
            if id_fantoir:
                fantoir = f"{id_fantoir[0:5]}{id_fantoir[6:10]}"
                # fantoir = topo.code_fantoir9_vers_fantoir10.get(fantoir9)
            else:
                fantoir = None
            self.add_adresse(
                Adresse(
                    self.code_insee,
                    lon,
                    lat,
                    numero,
                    "BAN",
                    voie=voie,
                    fantoir=fantoir,
                    code_postal=code_postal,
                    code_insee_ancienne_commune=code_insee_ancienne_commune,
                    nom_ancienne_commune=nom_ancienne_commune,
                )
            )

    def charge_numeros_osm(self):
        data = sql_get_data(
            "charge_numeros_OSM", dict(code_insee=self.code_insee)
        ) + sql_get_data("charge_numeros_bbox_OSM", dict(code_insee=self.code_insee))

        for (
            lon,
            lat,
            provenance,
            numero,
            voie,
            place,
            tags,
            suffixe,
            code_postal,
            code_insee_ancienne_commune,
            nom_ancienne_commune,
        ) in data:

            fantoir = tags.get("ref:FR:FANTOIR")
            if fantoir :
                fantoir = fantoir[0:9]
            if fantoir and not hp.fantoir_valide(fantoir, self.code_insee):
                continue

            if provenance in (
                1,
                2,
            ):
                self.add_adresse(
                    Adresse(
                        self.code_insee,
                        lon,
                        lat,
                        numero,
                        "OSM",
                        voie=voie,
                        place=place,
                        fantoir=fantoir,
                        code_postal=code_postal,
                        code_insee_ancienne_commune=code_insee_ancienne_commune,
                        nom_ancienne_commune=nom_ancienne_commune,
                    )
                )
            if provenance in (
                3,
                4,
            ) and tags.get("name"):
                self.add_adresse(
                    Adresse(
                        self.code_insee,
                        lon,
                        lat,
                        numero,
                        "OSM",
                        voie=tags["name"],
                        place=None,
                        fantoir=fantoir,
                        code_postal=code_postal,
                        code_insee_ancienne_commune=code_insee_ancienne_commune,
                        nom_ancienne_commune=nom_ancienne_commune,
                    )
                )
            if (
                provenance
                in (
                    5,
                    6,
                )
                and tags.get("name")
                and tags.get("ref:FR:FANTOIR")
            ):
                if tags["ref:FR:FANTOIR"][0:5] == self.code_insee:
                    self.add_adresse(
                        Adresse(
                            self.code_insee,
                            lon,
                            lat,
                            numero,
                            "OSM",
                            voie=tags["name"],
                            place=None,
                            fantoir=tags["ref:FR:FANTOIR"],
                            code_postal=code_postal,
                            code_insee_ancienne_commune=code_insee_ancienne_commune,
                            nom_ancienne_commune=nom_ancienne_commune,
                        )
                    )

    def noms_des_adresses(self, noms):
        for a in self:
            if a.voie:
                noms.add_nom(
                    Nom(
                        a.voie,
                        a.fantoir,
                        "voie",
                        a.source,
                        self.code_insee,
                        a.code_insee_ancienne_commune,
                        a.nom_ancienne_commune,
                    )
                )
            if a.place:
                noms.add_nom(
                    Nom(
                        a.place,
                        a.fantoir,
                        "place",
                        a.source,
                        self.code_insee,
                        a.code_insee_ancienne_commune,
                        a.nom_ancienne_commune,
                    )
                )

    def complete_fantoir(self, noms):
        for a in self:
            if a.fantoir:
                continue
            nom = a.voie or a.place
            if a.code_insee_ancienne_commune:
                a.fantoir = noms.fantoir_par_nom_sous_commune.get(
                    a.code_insee_ancienne_commune
                ).get(nom)
            else:
                a.fantoir = noms.fantoir_par_nom_sous_commune.get(nom)

    def enregistre(self):
        sql_process(
            "suppression_adresses_commune",
            dict(code_insee=self.code_insee),
        )
        io_in_csv = io.StringIO()

        for a in set(self.liste): #passage en set pour dedoublonner les adresses de provenances multiples
            io_in_csv.write(
                a._as_csv_format_bano() + "\n"
            )  # separateur $ car on trouve des virgules dans le contenu
        io_in_csv.seek(0)
        with bano_db.cursor() as cur_insert:
            cur_insert.copy_from(
                io_in_csv,
                "bano_adresses",
                null="",
                columns=(
                    "fantoir",
                    "lon",
                    "lat",
                    "numero",
                    "nom_voie",
                    "nom_place",
                    "code_postal",
                    "code_insee",
                    "code_insee_ancienne_commune",
                    "nom_ancienne_commune",
                    "source",
                ),
            )


class Point_nomme:
    def __init__(
        self,
        code_insee,
        source,
        nature,
        lon,
        lat,
        nom,
        fantoir=None,
        code_insee_ancienne_commune=None,
        nom_ancienne_commune=None,
    ):
        self.code_insee = code_insee
        self.source = source
        self.lon = round(lon, 6)
        self.lat = round(lat, 6)
        self.nature = nature
        self.nom = nom
        self.nom_normalise = hp.normalize(nom)
        self.fantoir = fantoir[0:9] if fantoir else None
        self.code_insee_ancienne_commune = code_insee_ancienne_commune
        self.nom_ancienne_commune = nom_ancienne_commune

    def __hash__(self):
        return hash(
            (self.code_insee, self.source, self.nom_normalise, self.code_insee_ancienne_commune)
        )

    def __eq__(self, other):
        return (
            self.code_insee == other.code_insee
            and self.source == other.source
            and self.nom_normalise == other.nom_normalise
            and self.code_insee_ancienne_commune == other.code_insee_ancienne_commune
        )

    def _as_string(self):
        return f"source : {self.source}, nom : {self.nom} ({self.nom_normalise}), nature : {self.nature}, sous_commune : {self.code_insee_ancienne_commune}"

    def _as_csv_format_bano(self):
        return f"{self.fantoir if self.fantoir else ''}\t{self.nom}\t{self.code_insee}\t{self.nature}\t{self.code_insee_ancienne_commune if self.code_insee_ancienne_commune else ''}\t{self.nom_ancienne_commune if self.nom_ancienne_commune else ''}\t{self.source}\t{self.lon}\t{self.lat}"


class Points_nommes:
    def __init__(self, code_insee):
        self.code_insee = code_insee
        self.liste = set()

    def __getitem__(self, key):
        return self.liste[key]

    def __iter__(self):
        return iter(self.liste)

    def _print(self, pattern=None):
        for a in self:
            if not pattern or pattern in a._as_string():
                print(a._as_string())

    def charge_points_nommes_lieux_dits_cadastre(self):
        data = sql_get_data(
            "charge_points_nommes_lieux-dits_CADASTRE",
            dict(code_insee=self.code_insee),
        )
        for x, y, nom, code_insee_ancienne_commune,nom_ancienne_commune in data:
            self.add_point_nomme(
                Point_nomme(
                    self.code_insee,
                    "CADASTRE",
                    "lieu-dit",
                    x,
                    y,
                    hp.format_toponyme(nom),
                    code_insee_ancienne_commune=code_insee_ancienne_commune,
                    nom_ancienne_commune=nom_ancienne_commune,
                )
            )

    def charge_points_nommes_centroides_osm(self):
        data = sql_get_data(
            "charge_points_nommes_centroides_OSM",
            dict(code_insee=self.code_insee),
        )
        for x, y, nom, code_insee_ancienne_commune, fantoir, nom_ancienne_commune in data:
            self.add_point_nomme(
                Point_nomme(
                    self.code_insee,
                    "OSM",
                    "centroide",
                    x,
                    y,
                    nom,
                    code_insee_ancienne_commune=code_insee_ancienne_commune,
                    fantoir=fantoir,
                    nom_ancienne_commune=nom_ancienne_commune,
                )
            )

    def charge_points_nommes_place_osm(self):
        data = sql_get_data(
            "charge_points_nommes_places_OSM",
            dict(code_insee=self.code_insee),
        )
        for x, y, nom, code_insee_ancienne_commune, fantoir, nom_ancienne_commune in data:
            self.add_point_nomme(
                Point_nomme(
                    self.code_insee,
                    "OSM",
                    "place",
                    x,
                    y,
                    nom,
                    code_insee_ancienne_commune=code_insee_ancienne_commune,
                    fantoir=fantoir,
                    nom_ancienne_commune=nom_ancienne_commune,
                )
            )

    def add_point_nomme(self, ld):
        self.liste.add(ld)

    def noms_des_points_nommes(self, noms):
        for a in self:
            if a.source == "CADASTRE":
                noms.add_nom(
                    Nom(
                        a.nom,
                        a.fantoir,
                        a.nature,
                        a.source,
                        self.code_insee,
                        a.code_insee_ancienne_commune,
                        a.nom_ancienne_commune,
                    )
                )
            if a.source == "OSM":
                noms.add_nom(
                    Nom(
                        a.nom,
                        a.fantoir,
                        a.nature,
                        a.source,
                        self.code_insee,
                        a.code_insee_ancienne_commune,
                        a.nom_ancienne_commune,
                    )
                )

    def complete_fantoir(self, noms):
        for a in self:
            if a.fantoir and a.fantoir[0:5] == self.code_insee:
                continue
            if a.code_insee_ancienne_commune:
                a.fantoir = noms.fantoir_par_nom_sous_commune.get(
                    a.code_insee_ancienne_commune
                ).get(a.nom)
            else:
                a.fantoir = noms.fantoir_par_nom_sous_commune.get(a.nom)

    def enregistre(self):
        sql_process(
            "suppression_points_nommes_commune",
            dict(code_insee=self.code_insee),
        )
        io_in_csv = io.StringIO()
        for t in self:
            io_in_csv.write(t._as_csv_format_bano() + "\n")
        io_in_csv.seek(0)
        with bano_db.cursor() as cur_insert:
            cur_insert.copy_from(
                io_in_csv,
                "bano_points_nommes",
                null="",
                columns=(
                    "fantoir",
                    "nom",
                    "code_insee",
                    "nature",
                    "code_insee_ancienne_commune",
                    "nom_ancienne_commune",
                    "source",
                    "lon",
                    "lat",
                ),
            )


class Topo:
    def __init__(self, code_insee):
        self.code_insee = code_insee
        self.topo = OrderedDict()
        # self.code_fantoir9_vers_fantoir10 = {}

        # self.index_by_nom_normalise = defaultdict(list)

        self.charge_topo()

    def __iter__(self):
        return iter(self.topo.items())

    # def __contains__(self, item):
    #     return item in self.a

    def __getitem__(self, key):
        return self.topo[key]

    def _print(self, pattern=None):
        for k, v in self:
            if not pattern or pattern in v:
                print(f"{k} : {v}")

    def charge_topo(self):
        data = sql_get_data("charge_topo_commune", dict(code_insee=self.code_insee))
        for fantoir, nom in data:
            nom = hp.normalize(" ".join(nom.replace("-", " ").split()))
            self.topo[fantoir] = nom
            # self.code_fantoir9_vers_fantoir10[fantoir[0:9]] = fantoir
            self.topo[nom] = fantoir

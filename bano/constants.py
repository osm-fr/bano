#!/usr/bin/env python
# coding: UTF-8

import json
from pathlib import Path


def load_pairs_from_file(basename):
    with (Path(__file__).parent / "dictionnaires" / f"{basename}.txt").open() as f:
        return [l[:-1].split("\t") for l in f.readlines() if not l.startswith("#")]


def load_json_from_file(json_filename):
    with (Path(__file__).parent / "data" / json_filename).open() as f:
        return json.loads(f.read())


def get_const_code_dir():
    return load_json_from_file("code_dir.json")


DEPARTEMENTS = [n.strip() for n in open('deplist.txt').readlines()]

DEPARTEMENTS_3CHAR = [("0" + s)[-3:] for s in DEPARTEMENTS]

LETTRE_A_LETTRE = {
    "A": ["Â", "À", "Á", "Ã"],
    "C": ["Ç"],
    "E": ["È", "Ê", "É", "Ë"],
    "I": ["Ï", "Î", "Í"],
    "N": ["Ñ"],
    "O": ["Ö", "Ô", "Ò", "Ó"],
    "U": ["Û", "Ü", "Ú"],
    "Y": ["Ÿ"],
    "OE": ["Œ"],
}

CHIFFRES = [
    ["0", "ZERO"],
    ["1", "UN"],
    ["2", "DEUX"],
    ["3", "TROIS"],
    ["4", "QUATRE"],
    ["5", "CINQ"],
    ["6", "SIX"],
    ["7", "SEPT"],
    ["8", "HUIT"],
    ["9", "NEUF"],
    [" DIX NEUF ", " UNNEUF "],
    [" DIX ", " UNZERO "],
    [" ONZE ", " UNUN "],
    [" DOUZE ", " UNDEUX "],
    [" TREIZE ", " UNTROIS "],
    [" QUATORZE ", " UNQUATRE "],
]

MOT_A_BLANC = ["DE LA", "DU", "DES", "LE", "LA", "LES", "DE", "D", "L"]

EXPAND_NOMS = load_pairs_from_file("expand_noms")
EXPAND_TITRES = load_pairs_from_file("expand_titres")
ABREV_TITRES = load_pairs_from_file("abrev_titres")
ABREV_TYPE_VOIE = dict(load_pairs_from_file("abrev_type_voie"))
SUBSTITUTION_COMPLETE = dict(load_pairs_from_file("substitution_complete"))
CHIFFRES_ROMAINS = dict(load_pairs_from_file("chiffres_romains"))

HIGHWAY_TYPES = [
    "steps",
    "path",
    "cycleway",
    "footway",
    "pedestrian",
    "track",
    "service",
    "road",
    "living_street",
    "residential",
    "unclassified",
    "tertiary",
    "secondary",
    "primary",
    "trunk",
    "motorway",
]
HIGHWAY_TYPES_INDEX = {e: 2**i for i, e in enumerate(HIGHWAY_TYPES)}

CODE_VOIE_FANTOIR = "0123456789ABCDEFGHIJKLMNOPQRSTVWXYZ"

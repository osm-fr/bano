import time
import os

from . import db
from .sql import sql_get_data


def liste_communes_par_dept(dept):
    return sql_get_data("liste_communes_par_dept", dict(dept=dept), db.bano)


def nom_commune(code_insee):
    return sql_get_data(
        "nom_commune_par_code_insee", dict(code_insee=code_insee), db.bano
    )[0][0]

import time
import os

from .sql import sql_get_data


def liste_communes_par_dept(dept):
    return sql_get_data("liste_communes_par_dept", dict(dept=dept))


def nom_commune(code_insee):
    res = sql_get_data("nom_commune_par_code_insee", dict(code_insee=code_insee))
    if res and len(res) > 0 and len(res[0]) > 0:
        return res[0][0]
    return f"Commune inconnue (INSEE {code_insee})"

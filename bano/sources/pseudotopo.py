from bano import db
from bano import models
from ..sql import sql_process,sql_get_data
from ..helpers import normalize,get_code_dept_from_insee
# from . import topo


def get_noms_ban_cadastre(code_insee):
    return sql_get_data('noms_ban_cadastre_non_rapproches_par_commune',dict(code_insee=code_insee))

def purge_noms_ban_cadastre_dans_topo(code_insee):
    sql_process('purge_noms_ban_cadastre_dans_topo',dict(code_insee=code_insee))

def add_noms_ban_cadastre_dans_topo(code_insee,noms_bc):
    sql_process('add_noms_ban_cadastre_dans_topo',dict(code_insee=code_insee,noms_bc=noms_bc))

def pseudo_fantoir(index,code_insee):
    return f"{code_insee}b{str(hex(index))[2:].ljust(3,'z')}"

def process(code_insee,**kwargs):
    purge_noms_ban_cadastre_dans_topo(code_insee)
    noms_bc = get_noms_ban_cadastre(code_insee)
    if len(noms_bc) > 0:
        topo = models.Topo(code_insee)
        dept = get_code_dept_from_insee(code_insee)

        noms_supplementaire = set()
        for i,n in enumerate(noms_bc):
            nom_norm = normalize(n[0])
            if not nom_norm in topo.topo:
                noms_supplementaire.add((nom_norm,n[1]))
        noms_bc_norm = []
        for i,nom_norm in enumerate(sorted(noms_supplementaire)):
            noms_bc_norm.append(f"'{dept}','{code_insee}','{pseudo_fantoir(i,code_insee)}',' ','{nom_norm[0]}','{nom_norm[1]}','{nom_norm[1]}','0000000'")

        if len(noms_bc_norm)>0:
            add_noms_ban_cadastre_dans_topo(code_insee, f"({'),('.join(noms_bc_norm)})")

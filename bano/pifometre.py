#!/usr/bin/env python
# coding: UTF-8

from . import batch as b
from .sql import sql_process


def process_croisement_voies_limites(departement, **kwargs):
    print(f"Traitement du dept {departement}")
    batch_id = b.batch_start_log("croisement_voies_limites", code_zone=departement)
    try:
        sql_process("croisement_voies_limites", dict(dept=departement))
        b.batch_stop_log(batch_id, True)
    except e:
        print(e)
        b.batch_stop_log(batch_id, False)

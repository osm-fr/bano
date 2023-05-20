#!/usr/bin/env python
# coding: UTF-8

import time
from .sql import sql_get_data, sql_process


def batch_start_log(etape, source=None, code_zone=None, nom_zone=None):
    t = time.localtime()
    date_debut = time.strftime("%d-%m-%Y %H:%M:%S", t)
    timestamp_debut = round(time.mktime(t), 0)

    champs = "etape,timestamp_debut,date_debut"
    values = f"'{etape}',{timestamp_debut},'{date_debut}'"
    if source:
        champs = f"{champs},source"
        values = f"{values},'{source}'"
    if code_zone:
        champs = f"{champs},code_zone"
        values = f"{values},'{code_zone}'"
    if nom_zone:
        champs = f"{champs},nom_zone"
        values = f"{values},'{nom_zone}'"
    return sql_get_data("batch_start_log", dict(etape=etape, code_zone=code_zone, champs=champs, values=values))[0][0]


def batch_stop_log(id_batch, status):
    t = time.localtime()
    date_fin = time.strftime("%d-%m-%Y %H:%M:%S", t)
    timestamp_fin = round(time.mktime(t), 0)
    sql_process(
        "batch_stop_log",
        dict(
            id_batch=str(id_batch),
            date_fin=str(date_fin),
            timestamp_fin=str(timestamp_fin),
            status=str(status),
        ),
    )
    if not status:
        print(f"Erreur pendant le processus {id_batch}")

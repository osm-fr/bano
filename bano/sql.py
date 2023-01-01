#!/usr/bin/env python
# coding: UTF-8

from pathlib import Path

from .db import bano_db

SQLDIR = Path(__file__).parent / "sql"


def sql_process(sqlfile, args):
    sqlfile = (Path(SQLDIR) / sqlfile).with_suffix(".sql")
    with open(sqlfile) as s:
        q = s.read()
        for k, v in args.items():
            q = q.replace(f"__{k}__", v)

    with bano_db.cursor() as cur:
        cur.execute(q)


def sql_get_data(sqlfile, args):
    sqlfile = (Path(SQLDIR) / sqlfile).with_suffix(".sql")
    with open(sqlfile) as s:
        q = s.read()
        for k, v in args.items():
            q = q.replace(f"__{k}__", v)

    with bano_db.cursor() as cur:
        cur.execute(q)

        return cur.fetchall()

    return None

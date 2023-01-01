#!/usr/bin/env python
# coding: UTF-8

from .db import bano_db
from .sql import sql_process


def setup_bano(**kwargs):
    sql_process("create_base", {}, bano_db)
    sql_process("create_table_base_bano_outils", {}, bano_db)
    sql_process("create_table_base_bano_sources", {}, bano_db)
    sql_process("create_table_base_bano_cog", {}, bano_db)
    sql_process("create_table_base_bano_cibles", {}, bano_db)

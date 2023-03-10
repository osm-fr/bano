#!/usr/bin/env python
# coding: UTF-8

from .db import bano_db
from .sql import sql_process


def setup_bano(**kwargs):
    sql_process("create_base", {})
    sql_process("create_table_base_bano_outils", {})
    sql_process("create_table_base_bano_sources", {})
    sql_process("create_table_base_bano_cog", {})
    sql_process("create_table_base_bano_cibles", {})

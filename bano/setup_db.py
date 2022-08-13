#!/usr/bin/env python
# coding: UTF-8

from . import db
from .sql import sql_process

def setup_bano_sources(**kwargs):
	sql_process('create_table_base_bano_sources',{},db.bano_sources)
#!/usr/bin/env python
# coding: UTF-8

import argparse
import sys

from . import setup_db
from .sources import topo


def main():
    parser = argparse.ArgumentParser(
        prog="bano", description="Donne accès à tous les traitements"
    )
    subparsers = parser.add_subparsers(help="Commandes disponibles")

    subparser = subparsers.add_parser(
        "setup_db_bano_sources",
        description="Initialisation de la BD des sources : OSM, BAN, TOPO",
    )
    subparser.set_defaults(func=setup_db.setup_bano_sources)

    subparser = subparsers.add_parser(
        "charge_topo",
        description="Charge une version du fichier TOPO",
    )
    subparser.set_defaults(func=topo.import_to_pg)

    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb

        ipdb.set_trace()

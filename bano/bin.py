#!/usr/bin/env python
# coding: UTF-8

import argparse
import sys

from . import setup_db
from .sources import topo,ban
from .constants import DEPARTEMENTS


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
        "setup_db_bano",
        description="Initialisation de la BD BANO",
    )
    subparser.set_defaults(func=setup_db.setup_bano)

    subparser = subparsers.add_parser(
        "charge_topo",
        description="Charge une version du fichier TOPO",
    )
    subparser.set_defaults(func=topo.process_topo)

    subparser = subparsers.add_parser(
        "charge_ban",
        description="Charge une version des fichiers BAN",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=ban.process_ban)

    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb

        ipdb.set_trace()

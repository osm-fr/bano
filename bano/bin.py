#!/usr/bin/env python
# coding: UTF-8

import argparse
import sys

from . import pre_process_suffixe
from . import setup_db
from .sources import topo,ban,cog
from .constants import DEPARTEMENTS


def main():
    parser = argparse.ArgumentParser(
        prog="bano", description="Donne accès à tous les traitements"
    )
    subparsers = parser.add_subparsers(help="Commandes disponibles")

    subparser = subparsers.add_parser(
        "setup_db_bano_sources",
        help="Initialisation de la BD des sources : OSM, BAN, TOPO",
    )
    subparser.set_defaults(func=setup_db.setup_bano_sources)

    subparser = subparsers.add_parser(
        "setup_db_bano",
        help="Initialisation de la BD BANO",
    )
    subparser.set_defaults(func=setup_db.setup_bano)

    subparser = subparsers.add_parser(
        "charge_topo",
        help="Charge une version du fichier TOPO",
    )
    subparser.set_defaults(func=topo.process_topo)

    subparser = subparsers.add_parser(
        "charge_cog",
        help="Charge une version des fichiers COG",
    )
    subparser.set_defaults(func=cog.process_cog)

    subparser = subparsers.add_parser(
        "charge_ban",
        help="Charge une version des fichiers BAN",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=ban.process_ban)

    subparser = subparsers.add_parser(
        "update_bis_table",
        help="Identifie les indices de répétition b,t,q assimilables à bis, ter, quater",
    )
    subparser.set_defaults(func=ban.update_bis_table)

    subparser = subparsers.add_parser(
        "pre_process_suffixe",
        help="Détermine les zones où les noms dans le Cadastre sont suffixés",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=pre_process_suffixe.process)


    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb

        ipdb.set_trace()

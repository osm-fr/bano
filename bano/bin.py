import argparse
import sys

from .constants import DEPARTEMENTS
from .core import addr_2_db
from .sources import bal


def main():
    parser = argparse.ArgumentParser(prog='bano', description='Donne accès à tous les traitements')
    subparsers = parser.add_subparsers(help='Commandes disponibles')
    subparser = subparsers.add_parser('process_commune', help='a help', description='Traite une commune')
    subparser.add_argument('source', choices=['OSM', 'CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('code_insee', type=str, help='Code INSEE de la commune à traiter')
    subparser.set_defaults(func=addr_2_db)
    subparser = subparsers.add_parser('download_bal', help='b help', description="Télécharge un fichier d'adresses")
    subparser.add_argument('source', choices=['CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=bal.process)

    args = parser.parse_args()
    # print(args)
    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))



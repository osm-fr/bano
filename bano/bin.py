import argparse
import sys

from .core import addr_2_db

def main():
    parser = argparse.ArgumentParser(prog='bano', description='Donne accès à tous les traitements')
    subparsers = parser.add_subparsers(help='Commandes disponibles')
    subparser = subparsers.add_parser('process_commune', help='a help', description='Traite une commune')
    subparser.add_argument('source', choices=['OSM', 'CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('code_insee', type=str, help='Code INSEE de la commune à traiter')
    subparser.set_defaults(func=addr_2_db)

    args = parser.parse_args()
    print(args)
    args.func(**vars(args))



import argparse
import sys

from .constants import DEPARTEMENTS
from .core import addr_2_db
from . import pre_process_suffixe
from .sources import bal, cadastre_gouv


def main():
    parser = argparse.ArgumentParser(prog='bano', description='Donne accès à tous les traitements')
    subparsers = parser.add_subparsers(help='Commandes disponibles')
    subparser = subparsers.add_parser('process_commune', help='a help', description='Traite une commune')
    subparser.add_argument('source', choices=['OSM', 'CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('code_insee', type=str, help='Code INSEE de la commune à traiter')
    subparser.set_defaults(func=addr_2_db)

    subparser = subparsers.add_parser('download_bal', help='b help', description="Met à jour les fichiers d'adresses au format BAL")
    subparser.add_argument('source', choices=['CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=bal.process)
    
    subparser = subparsers.add_parser('update_code_cadastre', help='b help', description="Met à jour la liste des communes d'après cadastre.gouv.fr")
    subparser.set_defaults(func=cadastre_gouv.process)
    
    subparser = subparsers.add_parser('pre_process_suffixe', help='b help', description="Détermine les zones où les noms dans le Cadastre sont suffixés")
    # subparser.add_argument('code_insee', type=str, help='Code INSEE de la commune à traiter')
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=pre_process_suffixe.process)

    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb; ipdb.set_trace()


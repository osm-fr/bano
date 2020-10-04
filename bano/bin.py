import argparse
import sys

from .constants import DEPARTEMENTS
from . import core, core_place, pre_process_suffixe, export, publish
from . import update_manager
from .sources import bal, cadastre_gouv, cadastre_json, ban


def main():
    parser = argparse.ArgumentParser(prog='bano', description='Donne accès à tous les traitements')
    subparsers = parser.add_subparsers(help='Commandes disponibles')

    subparser = subparsers.add_parser('process_commune', help='a help', description='Traite une commune')
    subparser.add_argument('source', choices=['OSM', 'CADASTRE', 'BAL','BAN'], type=str, help='Source des données à traiter')
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--code_insee', type=str, help='Code INSEE de la commune à traiter')
    group.add_argument('--depts', type=str, help='Départements à traiter', nargs='*')
    group.add_argument('--France', action='store_const', const=DEPARTEMENTS)
    subparser.set_defaults(func=core.process)

    subparser = subparsers.add_parser('process_commune_lieux-dits', help='a help', description='Traite une commune')
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('--code_insee', type=str, help='Code INSEE de la commune à traiter')
    group.add_argument('--depts', type=str, help='Départements à traiter', nargs='*')
    group.add_argument('--France', action='store_const', const=DEPARTEMENTS)
    subparser.set_defaults(func=core_place.process)

    subparser = subparsers.add_parser('download_bal', help='b help', description="Met à jour les fichiers d'adresses au format BAL")
    subparser.add_argument('source', choices=['CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=bal.process)
    
    subparser = subparsers.add_parser('download_ban', help='b help', description="Met à jour les fichiers d'adresses de source BAN")
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=ban.process)

    subparser = subparsers.add_parser('download_cadastre', help='b help', description="Met à jour les fichiers du cadastre hors adresses au format JSON")
    subparser.add_argument('prefixe', choices=['lieux_dits'], type=str, help='Source des données à traiter')
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=cadastre_json.process)

    subparser = subparsers.add_parser('update_code_cadastre', help='b help', description="Met à jour la liste des communes d'après cadastre.gouv.fr")
    subparser.set_defaults(func=cadastre_gouv.process)
    
    subparser = subparsers.add_parser('pre_process_suffixe', help='b help', description="Détermine les zones où les noms dans le Cadastre sont suffixés")
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=pre_process_suffixe.process)

    subparser = subparsers.add_parser('export', help='b help', description="Export par département dans différents formats")
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=export.process)

    subparser = subparsers.add_parser('publish', help='b help', description="Publication des exports dans un dossier web - fichiers par département")
    subparser.add_argument('departements', type=str, help='Départements à traiter', nargs='*', default=DEPARTEMENTS)
    subparser.set_defaults(func=publish.process)

    subparser = subparsers.add_parser('publish_aggregate', help='b help', description="Publication des exports dans un dossier web - fichiers France")
    subparser.set_defaults(func=publish.process_full)

    subparser = subparsers.add_parser('update_insee_lists', help='b help', description="Détermine les communes mises à jour grace aux tuiles impactées")
    subparser.set_defaults(func=update_manager.update_insee_lists)

    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb; ipdb.set_trace()


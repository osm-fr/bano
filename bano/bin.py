import argparse
import sys

from .constants import DEPARTEMENTS
from . import core, core_place, pre_process_suffixe, export, publish,debug
from . import update_manager
from .sources import bal, cadastre_gouv, cadastre_json, ban,ban2fantoir,datagouv_commune_summary as datagouv_cs


def main():
    parser = argparse.ArgumentParser(
        prog="bano", description="Donne accès à tous les traitements"
    )
    subparsers = parser.add_subparsers(help="Commandes disponibles")

    subparser = subparsers.add_parser(
        "process_commune",
        help="Traite unitairement les adresses d'une commune",
        description="Traite unitairement les adresses d'une commune",
    )
    subparser.add_argument(
        "source",
        choices=["OSM", "CADASTRE", "BAL", "BAN"],
        type=str,
        help="Source des données à traiter",
    )
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--code_insee", type=str, help="Code INSEE de la commune à traiter"
    )
    group.add_argument("--depts", type=str, help="Départements à traiter (toutes les communes de chaque dept sont traitées une par une)", nargs="*")
    group.add_argument("--France", help="Raccourci pour tous les départements d'un coup", action="store_const", const=DEPARTEMENTS)
    subparser.set_defaults(func=core.process)

    subparser = subparsers.add_parser(
        "process_commune_lieux-dits",
        help="Traite unitairement les lieux-dits d'une commune",
        description="Traite unitairement les lieux-dits d'une commune"
    )
    group = subparser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--code_insee", type=str, help="Code INSEE de la commune à traiter"
    )
    group.add_argument("--depts", type=str, help="Départements à traiter (toutes les communes de chaque dept sont traitées une par une)", nargs="*")
    group.add_argument("--France", help="Raccourci pour tous les départements d'un coup", action="store_const", const=DEPARTEMENTS)
    subparser.set_defaults(func=core_place.process)

    subparser = subparsers.add_parser(
        "download_commune_summary",
        help="Met à jour les stats de BAL",
        description="Met à jour les stats de BAL",
    )
    subparser.set_defaults(func=datagouv_cs.process)

    subparser = subparsers.add_parser(
        "ban2fantoir",
        help="Ajoute dans FANTOIR des libellés BAN",
        description="Ajoute dans FANTOIR des libellés BAN"
    )
    subparser.add_argument(
        "--code_insee", type=str, help="Code INSEE de la commune à traiter"
    )
    subparser.set_defaults(func=ban2fantoir.process)

    subparser = subparsers.add_parser(
        "download_bal",
        help="Met à jour les fichiers d'adresses au format BAL",
        description="Met à jour les fichiers d'adresses au format BAL",
    )
    subparser.add_argument(
        "source",
        choices=["CADASTRE", "BAL"],
        type=str,
        help="Source des données à traiter",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=bal.process)

    subparser = subparsers.add_parser(
        "download_ban",
        help="Met à jour les fichiers d'adresses de source BAN",
        description="Met à jour les fichiers d'adresses de source BAN",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=ban.process)

    subparser = subparsers.add_parser(
        "download_cadastre",
        help="Met à jour les fichiers du cadastre hors adresses au format JSON",
        description="Met à jour les fichiers du cadastre hors adresses au format JSON",
    )
    subparser.add_argument(
        "prefixe", choices=["lieux_dits"], type=str, help="Source des données à traiter"
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=cadastre_json.process)

    subparser = subparsers.add_parser(
        "update_code_cadastre",
        help="Met à jour la liste des communes d'après cadastre.gouv.fr - indique le format du Cadastre",
        description="Met à jour la liste des communes d'après cadastre.gouv.fr - indique le format du Cadastre",
    )
    subparser.set_defaults(func=cadastre_gouv.process)

    subparser = subparsers.add_parser(
        "update_bis_table",
        help="Identifie les indices de répétition b,t,q assimilables à bis, ter, quater",
        description="Identifie les indices de répétition b,t,q assimilables à bis, ter, quater",
    )
    subparser.set_defaults(func=ban.update_bis_table)

    subparser = subparsers.add_parser(
        "remove_chars_in_ban",
        help="ménage de caractères parasites dans les noms de voie BAN",
        description="ménage de caractères parasites dans les noms de voie BAN",
    )
    subparser.set_defaults(func=ban.remove_chars_in_ban)

    subparser = subparsers.add_parser(
        "pre_process_suffixe",
        help="Détermine les zones où les noms dans le Cadastre sont suffixés",
        description="Détermine les zones où les noms dans le Cadastre sont suffixés",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=pre_process_suffixe.process)

    subparser = subparsers.add_parser(
        "export",
        help="Export par département dans différents formats",
        description="Export par département dans différents formats",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=export.process)

    subparser = subparsers.add_parser(
        "publish",
        help="Publication des exports dans le dossier web de https://bano.openstreetmap.fr/data - fichiers par département",
        description="Publication des exports dans le dossier web de https://bano.openstreetmap.fr/data - fichiers par département",
    )
    subparser.add_argument(
        "departements",
        type=str,
        help="Départements à traiter",
        nargs="*",
        default=DEPARTEMENTS,
    )
    subparser.set_defaults(func=publish.process)

    subparser = subparsers.add_parser(
        "publish_aggregate",
        help="Publication des exports dans un dossier web - fichiers France entière",
        description="Publication des exports dans un dossier web - fichiers France entière",
    )
    subparser.set_defaults(func=publish.process_full)

    subparser = subparsers.add_parser(
        "update_insee_lists",
        help="Détermine les communes mises à jour grace aux tuiles impactées",
        description="Détermine les communes mises à jour grace aux tuiles impactées",
    )
    subparser.set_defaults(func=update_manager.update_insee_lists)

    subparser = subparsers.add_parser("debug_sql")
    subparser.add_argument("source",choices=["OSM", "BAN"],type=str,help="Source des données à traiter",)
    subparser.add_argument("code_insee", type=str, help="Code INSEE de la commune à traiter")
    subparser.set_defaults(func=debug.process_sql)

    args = parser.parse_args()

    try:
        args.func(**vars(args))
    except ValueError as err:
        sys.exit(str(err))
    except TypeError as err:
        import ipdb

        ipdb.set_trace()

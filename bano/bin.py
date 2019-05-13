import argparse
import sys

from .core import addr_2_db

def main():
    print("à table", sys.argv)
    parser = argparse.ArgumentParser(description='Traite une commune.')
    parser.add_argument('code_insee', type=str, help='Code INSEE de la commune à traiter')
    parser.add_argument('source', choices=['OSM', 'CADASTRE', 'BAL'], type=str, help='Source des données à traiter')
    # parser.add_argument('--sum', dest='accumulate', action='store_const',
    #                 const=sum, default=max,
    #                 help='sum the integers (default: find the max)')

    args = parser.parse_args()
    print(args)
    addr_2_db(**vars(args))

#!/usr/bin/env python
# coding: UTF-8
import os,os.path
import sys

def main(args):
    csvfile = open(args[1],'rb')
    # ligne d'entete
    l1 = csvfile.readline()

    previous_insee='0'
    dic_insee = {}
    output_file = None

    for l in csvfile:
        insee = l.split(';')[10]
        if insee != previous_insee:
            previous_insee = insee
            cache_dir = os.path.join(args[2],insee)
            if not os.path.exists(cache_dir):
                os.mkdir(cache_dir)
            if output_file:
                output_file.close()
            bal_output_filename = os.path.join(cache_dir,'{}-bal.csv'.format(insee))
            if insee in dic_insee:
                output_file = open(bal_output_filename,'ab')
            else:
                dic_insee[insee]=''
                output_file = open(bal_output_filename,'wb')
        output_file.write(l)
    if output_file:
        output_file.close()




if __name__ == '__main__':
    main(sys.argv)

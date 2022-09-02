#!/usr/bin/env python
# coding: UTF-8

from .models import Adresses, Topo

def process(source,code_insee,dept,**kwargs):
	# topo = Topo(code_insee)
	# topo._print('CO')
	adresses = Adresses(code_insee)
	adresses.charge_numeros_ban()
	adresses._print('Hell')
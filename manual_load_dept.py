import glob
import addr_2_db as a

rep_parcelles_adresses = 'parcelles_adresses'
list_txt = glob.glob('./'+rep_parcelles_adresses+'/[A-Z][A|B][0-9]*.txt')
for n in list_txt:
	code_cadastre = n.split('\\')[1].split('-')[0]
	code_insee = '92'+code_cadastre[2:5]
	a.main(['',code_insee,code_cadastre])
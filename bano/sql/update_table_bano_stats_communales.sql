DELETE FROM bano_stats_communales WHERE code_insee = '__code_insee__';
INSERT INTO bano_stats_communales VALUES ('__code_insee__',
	                                       __nb_adresses_osm__,
	                                       __nb_adresses_ban__,
	                                       __nb_noms_osm__,
	                                       __nb_noms_ban__,
	                                       __nb_noms_cadastre__,
	                                       __nb_noms_topo__);
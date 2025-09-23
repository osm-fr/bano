SELECT code_insee FROM topo_comparaison WHERE a_ajouter
UNION
SELECT code_insee FROM topo_comparaison WHERE a_maj;
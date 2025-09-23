DELETE FROM topo
WHERE code_insee IN (SELECT code_insee FROM topo_comparaison WHERE a_supprimer
                    UNION
                    SELECT code_insee FROM topo_comparaison WHERE a_maj);

INSERT INTO topo
SELECT *
FROM  topo_stage
WHERE code_insee IN (SELECT code_insee FROM topo_comparaison WHERE a_ajouter
                    UNION
                    SELECT code_insee FROM topo_comparaison WHERE a_maj);

DROP TABLE IF EXISTS topo_comparaison CASCADE;

CREATE TABLE topo_comparaison
AS
SELECT code_insee,code_insee AS code, 'communes apparues'  AS test,false::boolean AS a_supprimer,true::boolean AS a_ajouter,false::boolean AS a_maj FROM topo_stage
EXCEPT
SELECT code_insee,code_insee AS code, 'communes apparues'  AS test,false::boolean AS a_supprimer,true::boolean AS a_ajouter,false::boolean AS a_maj FROM topo       WHERE type_voie NOT IN ('B','C','T','F')
UNION ALL
SELECT code_insee,code_insee AS code, 'communes disparues' AS test,true::boolean AS a_supprimer,false::boolean AS a_ajouter,false::boolean AS a_maj FROM topo       WHERE type_voie NOT IN ('B','C','T','F')
EXCEPT
SELECT code_insee,code_insee AS code, 'communes disparues' AS test,true::boolean AS a_supprimer,false::boolean AS a_ajouter,false::boolean AS a_maj FROM topo_stage
UNION ALL
SELECT code_insee,fantoir    AS code, 'fantoirs apparus'   AS test,false::boolean AS a_supprimer,false::boolean AS a_ajouter,true::boolean AS a_maj FROM topo_stage
EXCEPT
SELECT code_insee,fantoir    AS code, 'fantoirs apparus'   AS test,false::boolean AS a_supprimer,false::boolean AS a_ajouter,true::boolean AS a_maj FROM topo       WHERE type_voie NOT IN ('B','C','T','F')
UNION ALL
SELECT code_insee,fantoir    AS code, 'fantoirs disparus'  AS test,false::boolean AS a_supprimer,false::boolean AS a_ajouter,true::boolean AS a_maj FROM topo       WHERE type_voie NOT IN ('B','C','T','F')
EXCEPT
SELECT code_insee,fantoir    AS code, 'fantoirs disparus'  AS test,false::boolean AS a_supprimer,false::boolean AS a_ajouter,true::boolean AS a_maj FROM topo_stage;
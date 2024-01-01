DROP TABLE IF EXISTS cog_pyramide_admin CASCADE;
CREATE TABLE cog_pyramide_admin
AS
SELECT com AS code_insee,
       typecom,
	   c.libelle AS nom_com,
       d.libelle AS nom_dep,
	   r.libelle AS nom_reg
FROM   cog_commune c
JOIN   (SELECT dep,libelle FROM cog_departement) d
USING  (dep)
JOIN   (SELECT reg,libelle FROM cog_region) r
USING  (reg);
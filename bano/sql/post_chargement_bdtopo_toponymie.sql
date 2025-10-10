DROP TABLE IF EXISTS bdtopo_toponymie_utile CASCADE;

CREATE TABLE bdtopo_toponymie_utile
AS
SELECT b.*,
       code_insee
FROM   (SELECT * FROM bdtopo_toponymie WHERE classe_de_l_objet = 'Zone d''habitation') b
JOIN   (SELECT geometrie,code_insee FROM polygones_insee WHERE admin_level = 8) p
ON	   ST_Intersects(b.geometrie, p.geometrie);

CREATE INDEX idx_bdtopo_toponymie_utile_code_insee ON bdtopo_toponymie_utile (code_insee);
CREATE INDEX gidx_bdtopo_toponymie_utile ON bdtopo_toponymie_utile USING GIST (geometrie);
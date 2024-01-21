DROP TABLE IF EXISTS insee_codes_postaux CASCADE;
CREATE TABLE insee_codes_postaux
AS
SELECT insee AS code_insee,
       STRING_AGG(cp,';') AS cps
FROM   (SELECT DISTINCT insee, cp FROM codes_postaux ORDER BY 1,2) AS c
GROUP BY 1;

CREATE INDEX idx_insee_codes_postaux_code_insee ON insee_codes_postaux(code_insee);

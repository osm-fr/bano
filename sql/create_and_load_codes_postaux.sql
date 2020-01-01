CREATE TEMP TABLE tmp_codes_postaux (raw text);
\copy tmp_codes_postaux FROM 'codes_postaux.csv' WITH csv HEADER delimiter '#';

CREATE TABLE IF NOT EXISTS codes_postaux(
	insee   text,
	commune text,
	cp      text,
	libelle text,
	ligne_5 text,
	geometrie geometry(Point,4326));

TRUNCATE codes_postaux;

WITH
a
AS
(SELECT string_to_array(raw,';') arr FROM tmp_codes_postaux)
INSERT INTO codes_postaux (insee,commune,cp,libelle,ligne_5,geometrie)
SELECT arr[1],
       arr[2],
       arr[3],
       arr[4],
       arr[5],
       ST_SetSRID(ST_Point((string_to_array(arr[6],','))[2]::float,(string_to_array(arr[6],','))[1]::float),4326)
FROM a;

CREATE INDEX IF NOT EXISTS gidx_codes_postaux ON codes_postaux USING GIST(geometrie);

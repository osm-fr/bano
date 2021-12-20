DROP TABLE IF EXISTS rep_b_as_bis CASCADE;
CREATE TABLE rep_b_as_bis
AS
SELECT  id_fantoir,
        numero
FROM    ban_odbl
WHERE   rep = 'b'

EXCEPT

(SELECT id_fantoir,
	    numero
FROM    ban_odbl
WHERE   rep = 'a'

UNION

SELECT  id_fantoir,
        numero
FROM    ban_odbl
WHERE   rep = 'c'

UNION

SELECT  id_fantoir,
        numero
FROM    ban_odbl
WHERE   rep = 'd');
COMMIT;
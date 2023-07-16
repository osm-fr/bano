DROP TABLE IF EXISTS rep_b_as_bis CASCADE;
CREATE TABLE rep_b_as_bis
AS
SELECT  fantoir,
        numero
FROM    ban
WHERE   rep = 'b'

EXCEPT

(SELECT fantoir,
	numero
FROM    ban
WHERE   rep = 'a'

UNION

SELECT  fantoir,
        numero
FROM    ban
WHERE   rep = 'c'

UNION

SELECT  fantoir,
        numero
FROM    ban
WHERE   rep = 'd');

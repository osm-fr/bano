INSERT INTO batch_historique
SELECT *
FROM batch
WHERE etape = '__etape__' AND
      code_zone = '__code_zone__';
DELETE FROM batch
WHERE etape = '__etape__' AND
      code_zone = '__code_zone__';
INSERT INTO batch(__champs__)
VALUES (__values__)
RETURNING id_batch;
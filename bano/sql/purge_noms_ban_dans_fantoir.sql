DELETE FROM fantoir_voie
WHERE code_insee = '__code_insee__' AND
      type_voie = 'B';
COMMIT;
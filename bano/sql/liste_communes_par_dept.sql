SELECT com,
       ncc
FROM   cog_commune c
LEFT OUTER JOIN (SELECT comparent FROM cog_commune WHERE dep = '__dept__' AND typecom = 'ARM') p
ON     (c.com = p.comparent)
WHERE  c.dep = '__dept__'  AND
       c.typecom != 'COMD' AND
       p.comparent IS NULL
ORDER BY 1

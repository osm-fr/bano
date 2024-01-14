SELECT id,
       citycode,
       type,
       name,
       postcode,
       lat,
       lon,
       city,
       departement,
       region,
       importance
FROM   export_voies_ld_sans_adresses_json
WHERE  dep = '__dept__'
ORDER BY 1;
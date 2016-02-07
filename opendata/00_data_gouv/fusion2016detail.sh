rm fusion2016detail.csv
wget https://raw.githubusercontent.com/cquest/fusion-communes-2016/master/fusion2016detail.csv
psql -f fusion2016detail.sql
psql cadastre -c "\\copy fusion2016detail from 'fusion2016detail.csv' with DELIMITER AS ',' csv header;"


psql -d cadastre -v ON_ERROR_STOP=1 -f stats.sql -v dept=$1

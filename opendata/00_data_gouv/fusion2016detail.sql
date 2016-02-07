DROP TABLE IF EXISTS fusion2016detail CASCADE;
CREATE TABLE fusion2016detail (
    dep text,
    nouvelle text,
    insee_nouvelle text,
    ancienne text,
    insee_ancienne text);
--COPY fusion2016detail FROM '/data/project/cadastre.openstreetmap.fr/export-cadastre/bin/cadastre-housenumber/bano/opendata/00_data_gouv/fusion2016detail.csv' WITH CSV HEADER;

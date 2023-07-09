CREATE TABLE IF NOT EXISTS cog_commune (
        typecom character(4),
        com character(5),
        reg character(2),
        dep character varying(3),
        ctcd character(4),
        arr character(4),
        tncc character(1),
        ncc text,
        nccenr text,
        libelle text,
        can character(5),
        comparent character(5));
CREATE INDEX IF NOT EXISTS idx_cog_commune_com ON cog_commune(com);
CREATE INDEX IF NOT EXISTS idx_cog_commune_dep ON cog_commune(dep);

CREATE TABLE IF NOT EXISTS cog_canton (
        can character(5),
        dep character varying(3),
        reg character(2),
        compct character(1),
        burcentral character(5),
        tncc character(1),
        ncc text,
        nccenr text,
        libelle text,
        typect character(1));
CREATE INDEX IF NOT EXISTS idx_cog_canton_can ON cog_canton(can);

CREATE TABLE IF NOT EXISTS cog_arrondissement (
        arr character(4),
        dep character varying(3),
        reg character(2),
        cheflieu character(5),
        tncc character(1),
        ncc text,
        nccenr text,
        libelle text);
CREATE INDEX IF NOT EXISTS idx_cog_arrondissement_arr ON cog_arrondissement(arr);

CREATE TABLE IF NOT EXISTS cog_departement (
        dep character varying(3),
        reg character(2),
        cheflieu character(5),
        tncc character(1),
        ncc text,
        nccenr text,
        libelle text);
CREATE INDEX IF NOT EXISTS idx_cog_departement_dep ON cog_departement(dep);

CREATE TABLE IF NOT EXISTS cog_region (
        reg character(2),
        cheflieu character(5),
        tncc character(1),
        ncc text,
        nccenr text,
        libelle text);
CREATE INDEX IF NOT EXISTS idx_cog_region_reg ON cog_region(reg);

GRANT SELECT ON ALL TABLES IN SCHEMA public TO public;
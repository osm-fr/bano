CREATE TABLE IF NOT EXISTS population_insee (
        insee_com character(5),
        nom text,
        population integer);
CREATE INDEX IF NOT EXISTS idx_population_insee_insee_com ON population_insee(insee_com);


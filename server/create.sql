-- Создание таблицы quality_index
CREATE TABLE quality_index (
    id_index SERIAL PRIMARY KEY,
    quality_index NUMERIC(10, 2) NOT NULL,
    data TIMESTAMP NOT NULL
);

-- Создание таблицы review
CREATE TABLE review (
    id_review SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    data_time TIMESTAMP NOT NULL,
    class VARCHAR(50) 
);

CREATE TABLE IF NOT EXISTS constellations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS stars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    const_id INTEGER NOT NULL,
    FOREIGN KEY (const_id) REFERENCES constellations (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS planets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    star_id INTEGER NOT NULL,
    FOREIGN KEY (star_id) REFERENCES stars (id) ON DELETE CASCADE
);

INSERT INTO constellations (name) VALUES
('Орион'), ('Лира'), ('Лебедь');
        
INSERT INTO stars (name, const_id) VALUES
('Бетельгейзе', 1),
('Вега', 2),
('Денеб', 3);
        
INSERT INTO planets (name, star_id) VALUES
('Аракис', 1), ('Каладан', 1), ('Гьеди Прайм', 1),
('Проксима', 2), ('Нова', 2), ('Терра', 2),
('Солярис', 3), ('Пандора', 3), ('Эгида', 3);
            
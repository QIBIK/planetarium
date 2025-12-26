"""
создать БД в соответствии с заданной предметной областью,
БД должна содержать не менее трех связанных таблиц,
заполнить таблицы БД информацией с помощью SQL-запросов,
инициализировать приложение FastAPI,
настроить соединение с базой данных,
определить endpoints для получения информации из всех таблиц, для добавления записей во все таблицы,
создать HTML форму для создания новых записей (использовать Jinja2 шаблоны с FastAPI),
осуществить экспорт и импорт одной любой таблицы из/в базу данных в формате xml.

ТЕМА: Планетарий
"""

import sqlite3
from fastapi.templating import Jinja2Templates
from fastapi import Request, FastAPI
from fastapi.responses import HTMLResponse


conn = sqlite3.connect('db.db')
cursor = conn.cursor()

# Включаем поддержку внешних ключей (чтобы связи работали)
cursor.execute("PRAGMA foreign_keys = ON;")

def get_db(table):
    conn = sqlite3.connect('db.db')
    # По стандарту row_factory использует кортежи, но благодаря Row будет более удобно 
    # Row - это умный объект, который помнит не только значение, но и имена колонок
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table}")
    # Закидываем в rows наш sql запрос 
    rows = cursor.fetchall() 
    # dict(row) превращает объект Row в обычный словарь
    result = [dict(row) for row in rows]
    conn.close()

    return result

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# @app.get("/constellations/{a}")
# async def read_constellations(a: int, b: str = None):
#     return {"hello": a, "b": b}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    constellations = get_db("constellations")
    stars = get_db("stars")
    planets = get_db("planets")
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "constellations": constellations,
        "stars": stars
    })

@app.get("/constellations")
async def read_constellations():
    result = get_db("constellations")
    return result

@app.get("/stars")
async def read_stars():
    result = get_db("stars")
    return result

@app.get("/planets")
async def read_planets():
    result = get_db("planets")
    return result

@app.post("/add_constellation")
async def add_const(name: str):
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO constellations (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    result = {"status": 200, "message": f"Добавлено в constellations {name}"}
    return result

@app.post("/add_star")
async def add_star(name: str, const_id: int):
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO stars (name, const_id) VALUES (?, ?)", (name, const_id))
    conn.commit()
    conn.close()
    result = {"status": 200, "message": f"Добавлено в stars {name} {const_id}"}
    return result

@app.post("/add_planet")
async def add_planet(name: str, star_id: int):
    conn = sqlite3.connect('db.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO planets (name, star_id) VALUES (?, ?)", (name, star_id))
    conn.commit()
    conn.close()
    result = {"status": 200, "message": f"Добавлено в planets {name} {star_id}"}
    return result


cursor.execute('''
CREATE TABLE IF NOT EXISTS constellations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS stars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    const_id INTEGER NOT NULL,
    FOREIGN KEY (const_id) REFERENCES constellations (id) ON DELETE CASCADE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS planets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    star_id INTEGER NOT NULL,
    FOREIGN KEY (star_id) REFERENCES stars (id) ON DELETE CASCADE
)
''')

try:
    cursor.execute("INSERT INTO constellations (name) VALUES "
    "('Орион'), ('Лира'), ('Лебедь')")
    
    cursor.execute("INSERT INTO stars (name, const_id) VALUES"
    "('Бетельгейзе', 1), "
    "('Вега', 2), "
    "('Денеб', 3)")
    
    cursor.execute("INSERT INTO planets (name, star_id) VALUES"
    "('Аракис', 1), ('Каладан', 1), ('Гьеди Прайм', 1),"
    "('Проксима', 2), ('Нова', 2), ('Терра', 2),"
    "('Солярис', 3), ('Пандора', 3), ('Эгида', 3);")
    
    conn.commit()

except:
    pass

"""
cursor.execute('''
    SELECT p.name, s.name, c.name 
    FROM planets p
    JOIN stars s ON p.star_id = s.id
    JOIN constellations c ON s.const_id = c.id
''')

for row in cursor.fetchall():
    print(f"Планета: {row[0]} | Звезда: {row[1]} | Созвездие: {row[2]}")
"""

conn.close()
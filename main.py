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

import xml.dom.minidom
import sqlite3
from fastapi.templating import Jinja2Templates
from fastapi import Request, FastAPI, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse

DB_PATH = "planetarium.db"
app = FastAPI()
templates = Jinja2Templates(directory="templates")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Включаем поддержку внешних ключей (чтобы связи работали)
    cursor.execute("PRAGMA foreign_keys = ON;")
    
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
        name TEXT NOT NULL UNIQUE,
        star_id INTEGER NOT NULL,
        FOREIGN KEY (star_id) REFERENCES stars (id) ON DELETE CASCADE
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM constellations")
    if cursor.fetchone()[0] == 0:
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
    conn.close()

init_db()

def get_db(table):
    conn = sqlite3.connect(DB_PATH)
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

@app.get("/export")
async def export_to_xml():
    data = get_db("constellations")
    file_name = "export_constellations.xml"

    # Создаем XML-документ
    doc = xml.dom.minidom.Document()

    # Создаем корневой элемент
    root = doc.createElement('table')
    doc.appendChild(root)

    for row in data:
        record = doc.createElement("record")
        root.appendChild(record)

        for key, value in row.items():
            element = doc.createElement(key)
            element.appendChild(doc.createTextNode(str(value)))
            record.appendChild(element)

    with open(file_name, "w", encoding="UTF-8") as f:
        f.write(doc.toprettyxml()) # toprettyxml преобразует в красоту

    return FileResponse(file_name, filename=file_name)

@app.post("/import")
async def import_from_xml(file: UploadFile = File(...)):
    # await дожидаемся полного скачивания файла
    content = await file.read()
    xml_file = "table.xml"
    with open(xml_file, "wb") as f:
        f.write(content)

    doc = xml.dom.minidom.parse(xml_file)
    
    constellations_list = doc.getElementsByTagName('record')

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for item in constellations_list:
        name_elements = item.getElementsByTagName('name')
        
        if name_elements and name_elements[0].childNodes:
            name_node = name_elements[0].childNodes[0]
            # Используем .nodeValue — это более универсальный способ достать текст в DOM
            name = str(name_node.nodeValue)
            
            cursor.execute("INSERT OR IGNORE INTO constellations (name) VALUES (?)", (name,))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/?success=1", status_code=303)

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request, success: int = 0):
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "constellations": get_db("constellations"),
        "stars": get_db("stars"),
        "planets": get_db("planets"),
        "success": success
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
async def add_const(name: str = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO constellations (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/?success=1", status_code=303)

@app.post("/add_star")
async def add_star(name: str = Form(...), const_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO stars (name, const_id) VALUES (?, ?)", (name, const_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/?success=1", status_code=303)

@app.post("/add_planet")
async def add_planet(name: str = Form(...), star_id: int = Form(...)):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(f"INSERT INTO planets (name, star_id) VALUES (?, ?)", (name, star_id))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/?success=1", status_code=303)

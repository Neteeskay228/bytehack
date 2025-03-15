import aiosqlite
import asyncio
from flask import Flask, request, jsonify

app = Flask(__name__)

class ImageDatabase:
    def __init__(self, db_name="image_data.db"):
        self.db_name = db_name

    async def initialize(self):
        await self.create_table()

    async def create_table(self):
        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    objects TEXT,
                    extracted_text TEXT
                )
            ''')
            await db.commit()

    async def save_image_data(self, filename, objects, extracted_text):
        await self.initialize()

        async with aiosqlite.connect(self.db_name) as db:
            await db.execute('''
                INSERT INTO images (filename, objects, extracted_text) 
                VALUES (?, ?, ?)
            ''', (filename, objects, extracted_text))
            await db.commit()

    async def search(self, search_query):
        await self.initialize()
        async with aiosqlite.connect(self.db_name) as db:
            cursor = await db.execute('''
                SELECT * FROM images 
                WHERE extracted_text LIKE ? OR objects LIKE ?
            ''', ('%' + search_query + '%', '%' + search_query + '%'))
            rows = await cursor.fetchall()
            return rows
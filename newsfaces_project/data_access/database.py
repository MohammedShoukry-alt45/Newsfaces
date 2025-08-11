import sqlite3
import json
import traceback
from config import settings


class DatabaseManager:
    def __init__(self, db_path=settings.DB_PATH):
        self.db_path = db_path
        self.init_database()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    # Initialize tables for database
    def init_database(self):

        try:
            conn = self._connect()
            cursor = conn.cursor()

            # Articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_uri TEXT,
                    title TEXT,
                    cleaned_text TEXT,
                    language TEXT,
                    sentiment_label TEXT,
                    sentiment_score REAL,
                    topic_category TEXT,
                    keywords TEXT,
                    person_entities TEXT,
                    org_entities TEXT,
                    location_entities TEXT
                )
            ''')

            # Images table in
            #TODO add face count ,detected faces , genrated name for image in nex phases
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    image_path TEXT,
                    FOREIGN KEY(article_id) REFERENCES articles(article_id)
                )
            ''')

            # Known faces table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS known_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    encoding TEXT
                )
            ''')

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error initializing database: {e}")
            traceback.print_exc()

    # Insert article into reduced schema
    def insert_article(self, article_data):

        try:
            conn = self._connect()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO articles (
                    target_uri, title, cleaned_text, language, sentiment_label,
                    sentiment_score, topic_category, keywords,
                    person_entities, org_entities, location_entities
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article_data.get('target_uri'),
                article_data.get('title'),
                article_data.get('cleaned_text'),
                article_data.get('language'),
                article_data.get('sentiment_label'),
                article_data.get('sentiment_score'),
                article_data.get('topic_category'),
                json.dumps(article_data.get('keywords', []), ensure_ascii=False)
                    if not isinstance(article_data.get('keywords'), str)
                    else article_data.get('keywords'),
                json.dumps(article_data.get('person_entities', []), ensure_ascii=False)
                    if not isinstance(article_data.get('person_entities'), str)
                    else article_data.get('person_entities'),
                json.dumps(article_data.get('org_entities', []), ensure_ascii=False)
                    if not isinstance(article_data.get('org_entities'), str)
                    else article_data.get('org_entities'),
                json.dumps(article_data.get('location_entities', []), ensure_ascii=False)
                    if not isinstance(article_data.get('location_entities'), str)
                    else article_data.get('location_entities')
            ))

            article_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return article_id

        except Exception as e:
            print(f"Error inserting article: {e}")
            traceback.print_exc()
            return None

    def insert_image(self, article_id, image_path):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO images (article_id, image_path)
            VALUES (?, ?)
        ''', (article_id, image_path))
        conn.commit()
        conn.close()

    def insert_face_encoding(self, name, encoding):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO known_faces (name, encoding)
            VALUES (?, ?)
        ''', (name, json.dumps(encoding)))
        conn.commit()
        conn.close()

    def get_article_count(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM articles')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_image_count(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM images')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_known_faces_count(self):
        conn = self._connect()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(DISTINCT name) FROM known_faces')
        count = cursor.fetchone()[0]
        conn.close()
        return count

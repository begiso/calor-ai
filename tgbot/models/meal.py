import sqlite3
import json
from datetime import datetime, date
from typing import Optional, List, Dict
from pathlib import Path


class MealModel:
    """Модель для работы с приемами пищи"""

    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Инициализация таблиц для приемов пищи"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            # Таблица приемов пищи
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meals (
                    meal_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    meal_date DATE NOT NULL,
                    status TEXT DEFAULT 'draft',
                    total_calories INTEGER DEFAULT 0,
                    total_proteins REAL DEFAULT 0,
                    total_fats REAL DEFAULT 0,
                    total_carbs REAL DEFAULT 0,
                    photo_file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Таблица продуктов в приемах пищи
            conn.execute("""
                CREATE TABLE IF NOT EXISTS meal_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    meal_id INTEGER NOT NULL,
                    product_name TEXT NOT NULL,
                    weight INTEGER NOT NULL,
                    calories INTEGER NOT NULL,
                    proteins REAL NOT NULL,
                    fats REAL NOT NULL,
                    carbs REAL NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (meal_id) REFERENCES meals (meal_id) ON DELETE CASCADE
                )
            """)

            # Индексы для быстрого поиска
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_user_date
                ON meals(user_id, meal_date)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_meals_status
                ON meals(status)
            """)

            conn.commit()

    def create_meal(self, user_id: int, photo_file_id: str,
                   meal_date: Optional[date] = None) -> int:
        """Создать новый прием пищи со статусом draft"""
        if meal_date is None:
            meal_date = date.today()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO meals (user_id, meal_date, photo_file_id, status)
                VALUES (?, ?, ?, 'draft')
            """, (user_id, meal_date.isoformat(), photo_file_id))
            conn.commit()
            return cursor.lastrowid

    def add_meal_item(self, meal_id: int, product_name: str, weight: int,
                     calories: int, proteins: float, fats: float,
                     carbs: float, confidence: float = 1.0):
        """Добавить продукт в прием пищи"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO meal_items
                (meal_id, product_name, weight, calories, proteins, fats, carbs, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (meal_id, product_name, weight, calories, proteins, fats, carbs, confidence))

            # Обновляем итоговые значения приема пищи
            conn.execute("""
                UPDATE meals
                SET total_calories = (
                        SELECT SUM(calories) FROM meal_items WHERE meal_id = ?
                    ),
                    total_proteins = (
                        SELECT SUM(proteins) FROM meal_items WHERE meal_id = ?
                    ),
                    total_fats = (
                        SELECT SUM(fats) FROM meal_items WHERE meal_id = ?
                    ),
                    total_carbs = (
                        SELECT SUM(carbs) FROM meal_items WHERE meal_id = ?
                    ),
                    updated_at = ?
                WHERE meal_id = ?
            """, (meal_id, meal_id, meal_id, meal_id, datetime.now(), meal_id))

            conn.commit()

    def get_meal(self, meal_id: int) -> Optional[Dict]:
        """Получить прием пищи по ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Получаем данные приема пищи
            cursor = conn.execute("""
                SELECT * FROM meals WHERE meal_id = ?
            """, (meal_id,))
            meal_row = cursor.fetchone()

            if not meal_row:
                return None

            meal = dict(meal_row)

            # Получаем продукты
            cursor = conn.execute("""
                SELECT * FROM meal_items WHERE meal_id = ?
            """, (meal_id,))
            items = [dict(row) for row in cursor.fetchall()]
            meal['items'] = items

            return meal

    def get_user_draft_meal(self, user_id: int) -> Optional[Dict]:
        """Получить незавершенный прием пищи пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT meal_id FROM meals
                WHERE user_id = ? AND status = 'draft'
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            row = cursor.fetchone()

            if row:
                return self.get_meal(row['meal_id'])
            return None

    def update_meal_item(self, item_id: int, weight: Optional[int] = None,
                        calories: Optional[int] = None, proteins: Optional[float] = None,
                        fats: Optional[float] = None, carbs: Optional[float] = None):
        """Обновить данные продукта в приеме пищи"""
        with sqlite3.connect(self.db_path) as conn:
            # Получаем meal_id для обновления итогов
            cursor = conn.execute("SELECT meal_id FROM meal_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return

            meal_id = row[0]

            # Обновляем только переданные поля
            fields = []
            values = []

            if weight is not None:
                fields.append("weight = ?")
                values.append(weight)
            if calories is not None:
                fields.append("calories = ?")
                values.append(calories)
            if proteins is not None:
                fields.append("proteins = ?")
                values.append(proteins)
            if fats is not None:
                fields.append("fats = ?")
                values.append(fats)
            if carbs is not None:
                fields.append("carbs = ?")
                values.append(carbs)

            if fields:
                values.append(item_id)
                conn.execute(f"""
                    UPDATE meal_items SET {', '.join(fields)}
                    WHERE item_id = ?
                """, values)

                # Обновляем итоги приема пищи
                conn.execute("""
                    UPDATE meals
                    SET total_calories = (
                            SELECT SUM(calories) FROM meal_items WHERE meal_id = ?
                        ),
                        total_proteins = (
                            SELECT SUM(proteins) FROM meal_items WHERE meal_id = ?
                        ),
                        total_fats = (
                            SELECT SUM(fats) FROM meal_items WHERE meal_id = ?
                        ),
                        total_carbs = (
                            SELECT SUM(carbs) FROM meal_items WHERE meal_id = ?
                        ),
                        updated_at = ?
                    WHERE meal_id = ?
                """, (meal_id, meal_id, meal_id, meal_id, datetime.now(), meal_id))

                conn.commit()

    def delete_meal_item(self, item_id: int):
        """Удалить продукт из приема пищи"""
        with sqlite3.connect(self.db_path) as conn:
            # Получаем meal_id
            cursor = conn.execute("SELECT meal_id FROM meal_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if not row:
                return

            meal_id = row[0]

            # Удаляем продукт
            conn.execute("DELETE FROM meal_items WHERE item_id = ?", (item_id,))

            # Обновляем итоги
            conn.execute("""
                UPDATE meals
                SET total_calories = COALESCE((
                        SELECT SUM(calories) FROM meal_items WHERE meal_id = ?
                    ), 0),
                    total_proteins = COALESCE((
                        SELECT SUM(proteins) FROM meal_items WHERE meal_id = ?
                    ), 0),
                    total_fats = COALESCE((
                        SELECT SUM(fats) FROM meal_items WHERE meal_id = ?
                    ), 0),
                    total_carbs = COALESCE((
                        SELECT SUM(carbs) FROM meal_items WHERE meal_id = ?
                    ), 0),
                    updated_at = ?
                WHERE meal_id = ?
            """, (meal_id, meal_id, meal_id, meal_id, datetime.now(), meal_id))

            conn.commit()

    def confirm_meal(self, meal_id: int):
        """Подтвердить прием пищи (изменить статус на confirmed)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE meals
                SET status = 'confirmed', updated_at = ?
                WHERE meal_id = ?
            """, (datetime.now(), meal_id))
            conn.commit()

    def cancel_meal(self, meal_id: int):
        """Отменить прием пищи (удалить)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM meals WHERE meal_id = ?", (meal_id,))
            conn.commit()

    def get_daily_stats(self, user_id: int, meal_date: Optional[date] = None) -> Dict:
        """Получить статистику по приемам пищи за день"""
        if meal_date is None:
            meal_date = date.today()

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT
                    COALESCE(SUM(total_calories), 0) as total_calories,
                    COALESCE(SUM(total_proteins), 0) as total_proteins,
                    COALESCE(SUM(total_fats), 0) as total_fats,
                    COALESCE(SUM(total_carbs), 0) as total_carbs,
                    COUNT(*) as meal_count
                FROM meals
                WHERE user_id = ? AND meal_date = ? AND status = 'confirmed'
            """, (user_id, meal_date.isoformat()))

            row = cursor.fetchone()
            return dict(row) if row else {
                'total_calories': 0,
                'total_proteins': 0,
                'total_fats': 0,
                'total_carbs': 0,
                'meal_count': 0
            }

    def get_user_meals(self, user_id: int, meal_date: Optional[date] = None,
                      status: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Получить список приемов пищи пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            query = "SELECT * FROM meals WHERE user_id = ?"
            params = [user_id]

            if meal_date:
                query += " AND meal_date = ?"
                params.append(meal_date.isoformat())

            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)

            cursor = conn.execute(query, params)
            meals = []

            for row in cursor.fetchall():
                meal = dict(row)
                # Получаем продукты для каждого приема
                items_cursor = conn.execute("""
                    SELECT * FROM meal_items WHERE meal_id = ?
                """, (meal['meal_id'],))
                meal['items'] = [dict(item) for item in items_cursor.fetchall()]
                meals.append(meal)

            return meals

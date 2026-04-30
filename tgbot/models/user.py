import sqlite3
from datetime import datetime, date
from typing import Optional
from pathlib import Path


class UserModel:
    """Модель пользователя для работы с SQLite"""
    
    def __init__(self, db_path: str = "data/database.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация базы данных и создание таблицы"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'ru',
                    gender TEXT,
                    birth_date DATE,
                    height INTEGER,
                    weight REAL,
                    activity_level INTEGER,
                    daily_calories INTEGER,
                    daily_proteins REAL,
                    daily_fats REAL,
                    daily_carbs REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Создаем индекс для ускорения запросов по языку
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_language
                ON users(language)
            """)

            conn.commit()
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Получить данные пользователя"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM users WHERE user_id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def create_or_update_user(self, user_id: int, **kwargs) -> dict:
        """Создать или обновить пользователя"""
        user = self.get_user(user_id)
        
        # Конвертируем date в строку для SQLite
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, date):
                processed_kwargs[key] = value.isoformat()
            else:
                processed_kwargs[key] = value
        
        with sqlite3.connect(self.db_path) as conn:
            if user:
                # Обновление
                fields = []
                values = []
                for key, value in processed_kwargs.items():
                    if value is not None:
                        fields.append(f"{key} = ?")
                        values.append(value)
                
                if fields:
                    fields.append("updated_at = ?")
                    values.append(datetime.now())
                    values.append(user_id)
                    
                    conn.execute(
                        f"UPDATE users SET {', '.join(fields)} WHERE user_id = ?",
                        values
                    )
            else:
                # Создание
                fields = ["user_id"] + list(processed_kwargs.keys())
                placeholders = ["?"] * len(fields)
                values = [user_id] + [processed_kwargs.get(field) for field in fields[1:]]
                
                conn.execute(
                    f"INSERT INTO users ({', '.join(fields)}) VALUES ({', '.join(placeholders)})",
                    values
                )
            conn.commit()
        
        return self.get_user(user_id)
    
    def is_onboarding_complete(self, user_id: int) -> bool:
        """Проверить, завершен ли онбординг"""
        user = self.get_user(user_id)
        if not user:
            return False

        required_fields = ['gender', 'birth_date', 'height', 'weight', 'activity_level']
        # ВАЖНО: используем 'is not None' вместо просто проверки значения,
        # потому что activity_level может быть 0, что является валидным значением
        return all(user.get(field) is not None for field in required_fields)
    
    def reset_onboarding(self, user_id: int):
        """Сбросить данные онбординга для пересчета"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE users 
                SET gender = NULL, 
                    birth_date = NULL, 
                    height = NULL, 
                    weight = NULL, 
                    activity_level = NULL,
                    updated_at = ?
                WHERE user_id = ?
            """, (datetime.now(), user_id))
            conn.commit()

    def get_total_users_count(self) -> int:
        """Получить общее количество пользователей"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            return cursor.fetchone()[0]

    def get_completed_onboarding_count(self) -> int:
        """Получить количество пользователей, завершивших онбординг"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM users
                WHERE gender IS NOT NULL
                AND birth_date IS NOT NULL
                AND height IS NOT NULL
                AND weight IS NOT NULL
                AND activity_level IS NOT NULL
            """)
            return cursor.fetchone()[0]

    def get_users_by_language(self) -> dict:
        """Получить количество пользователей по языкам"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT language, COUNT(*) as count
                FROM users
                GROUP BY language
            """)
            return {row[0]: row[1] for row in cursor.fetchall()}


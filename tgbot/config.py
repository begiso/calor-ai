import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class DbConfig:
    """
    SQLite database configuration class.
    
    Attributes
    ----------
    path : str
        Path to the SQLite database file.
    """
    path: str = "data/database.db"

    @staticmethod
    def from_env():
        """
        Creates the DbConfig object from environment variables.
        """
        db_path = os.getenv("DB_PATH", "data/database.db")
        # Создаём директорию для БД если её нет
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        return DbConfig(path=db_path)


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]

    @staticmethod
    def from_env():
        """
        Creates the TgBot object from environment variables.
        """
        # Debug: print all environment variables to see what's available
        import sys
        print("DEBUG: Checking environment variables...", file=sys.stderr)
        print(f"DEBUG: BOT_TOKEN exists: {bool(os.getenv('BOT_TOKEN'))}", file=sys.stderr)
        print(f"DEBUG: All env vars starting with BOT: {[k for k in os.environ.keys() if 'BOT' in k or 'TOKEN' in k]}", file=sys.stderr)

        token = os.getenv("BOT_TOKEN")
        if not token:
            raise ValueError("BOT_TOKEN не найден в переменных окружения")

        admins_str = os.getenv("ADMINS", "")
        admin_ids = [int(admin_id.strip()) for admin_id in admins_str.split(",") if admin_id.strip()]

        return TgBot(token=token, admin_ids=admin_ids)


@dataclass
class Miscellaneous:
    """
    Miscellaneous configuration class.

    This class holds settings for various other parameters.
    It merely serves as a placeholder for settings that are not part of other categories.

    Attributes
    ----------
    other_params : str, optional
        A string used to hold other various parameters as required (default is None).
    """

    other_params: str = None


@dataclass
class Config:
    """
    The main configuration class that integrates all the other configuration classes.

    This class holds the other configuration classes, providing a centralized point of access for all settings.

    Attributes
    ----------
    tg_bot : TgBot
        Holds the settings related to the Telegram Bot.
    misc : Miscellaneous
        Holds the values for miscellaneous settings.
    db : Optional[DbConfig]
        Holds the settings specific to the database (default is None).
    """

    tg_bot: TgBot
    misc: Miscellaneous
    db: Optional[DbConfig] = None


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """
    # Загружаем переменные окружения из .env файла (только если файл существует)
    import os.path
    if path and os.path.exists(path):
        load_dotenv(path)
    elif os.path.exists(".env"):
        load_dotenv()
    # Если .env не существует, используем переменные окружения системы (Railway, Render, etc.)

    return Config(
        tg_bot=TgBot.from_env(),
        db=DbConfig.from_env(),
        misc=Miscellaneous(),
    )

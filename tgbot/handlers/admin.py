import os
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.models.user import UserModel
from tgbot.models.meal import MealModel

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.reply("👨‍💼 Панель администратора\n\n"
                       "Доступные команды:\n"
                       "/admin - эта панель\n"
                       "/stats - статистика бота\n"
                       "/dbclear - очистить базу данных")


@admin_router.message(Command("stats"))
async def show_stats(message: Message):
    """Показать статистику бота (только для админа)"""
    try:
        user_model = UserModel()
        meal_model = MealModel()

        # Собираем статистику
        total_users = user_model.get_total_users_count()
        completed_users = user_model.get_completed_onboarding_count()
        users_by_lang = user_model.get_users_by_language()

        # Получаем статистику по приемам пищи
        from datetime import datetime
        import sqlite3
        today = datetime.now().date().isoformat()

        # Подсчитываем приемы пищи за сегодня
        with sqlite3.connect(user_model.db_path) as conn:
            cursor = conn.execute("""
                SELECT COUNT(DISTINCT user_id) as active_users_today
                FROM meals
                WHERE DATE(created_at) = ?
                AND status = 'confirmed'
            """, (today,))
            result = cursor.fetchone()
            active_today = result[0] if result else 0

            cursor = conn.execute("""
                SELECT COUNT(*) as total_meals
                FROM meals
                WHERE status = 'confirmed'
            """)
            result = cursor.fetchone()
            total_meals = result[0] if result else 0

        # Форматируем статистику
        stats_text = "📊 <b>Статистика бота</b>\n\n"
        stats_text += f"👥 <b>Всего пользователей:</b> {total_users}\n"
        stats_text += f"✅ <b>Завершили регистрацию:</b> {completed_users}\n"
        stats_text += f"⏳ <b>Не завершили:</b> {total_users - completed_users}\n\n"

        stats_text += "<b>📊 По языкам:</b>\n"
        for lang, count in users_by_lang.items():
            lang_name = "🇷🇺 Русский" if lang == "ru" else "🇺🇿 O'zbek"
            stats_text += f"  {lang_name}: {count}\n"

        stats_text += f"\n<b>🍽 Приемы пищи:</b>\n"
        stats_text += f"  Всего подтверждено: {total_meals}\n"
        stats_text += f"  Активных сегодня: {active_today}"

        await message.reply(stats_text, parse_mode='HTML')

    except Exception as e:
        await message.reply(f"❌ Ошибка при получении статистики:\n{str(e)}")


@admin_router.message(Command("dbclear"))
async def clear_database(message: Message):
    """Очистка базы данных (только для админа)"""
    try:
        db_path = "data/database.db"

        if os.path.exists(db_path):
            os.remove(db_path)
            await message.reply("✅ База данных успешно удалена!\n\n"
                              "Она будет создана заново при следующем запуске бота.")
        else:
            await message.reply("⚠️ База данных не найдена по пути: " + db_path)

    except Exception as e:
        await message.reply(f"❌ Ошибка при удалении базы данных:\n{str(e)}")

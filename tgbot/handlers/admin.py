import os
import sqlite3
from datetime import datetime, date

from aiogram import Router
from aiogram.filters import Command, CommandObject
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
                       "/user <code>ID</code> - инфо о пользователе\n"
                       "/dbclear - очистить базу данных",
                       parse_mode='HTML')


@admin_router.message(Command("user"))
async def user_info(message: Message, command: CommandObject):
    """Информация о конкретном пользователе по ID"""
    if not command.args:
        await message.reply("Использование: /user <code>ID</code>\nПример: /user 123456789", parse_mode='HTML')
        return

    try:
        target_id = int(command.args.strip())
    except ValueError:
        await message.reply("❌ ID должен быть числом.")
        return

    user_model = UserModel()
    meal_model = MealModel()
    user = user_model.get_user(target_id)

    if not user:
        await message.reply(f"❌ Пользователь <code>{target_id}</code> не найден.", parse_mode='HTML')
        return

    gender_map = {"male": "👨 Мужчина", "female": "👩 Женщина"}
    lang_map = {"ru": "🇷🇺 Русский", "uz": "🇺🇿 O'zbek"}

    # Возраст
    age = "—"
    if user.get('birth_date'):
        try:
            bd = datetime.strptime(user['birth_date'], "%Y-%m-%d").date()
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
        except Exception:
            age = "—"

    # Статистика приёмов пищи
    today_stats = meal_model.get_daily_stats(target_id)
    with sqlite3.connect(user_model.db_path) as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM meals WHERE user_id = ? AND status = 'confirmed'",
            (target_id,)
        )
        total_meals = cursor.fetchone()[0]

    onboarding = "✅" if user_model.is_onboarding_complete(target_id) else "❌"

    text = (
        f"👤 <b>Пользователь</b> <code>{target_id}</code>\n\n"
        f"<b>Профиль:</b>\n"
        f"  Язык: {lang_map.get(user.get('language'), '—')}\n"
        f"  Пол: {gender_map.get(user.get('gender'), '—')}\n"
        f"  Возраст: {age}\n"
        f"  Рост: {user.get('height') or '—'} см\n"
        f"  Вес: {user.get('weight') or '—'} кг\n"
        f"  Онбординг: {onboarding}\n\n"
        f"<b>Норма:</b>\n"
        f"  🔥 {user.get('daily_calories') or 0} ккал\n"
        f"  Б: {user.get('daily_proteins') or 0} г | "
        f"Ж: {user.get('daily_fats') or 0} г | "
        f"У: {user.get('daily_carbs') or 0} г\n\n"
        f"<b>Сегодня:</b>\n"
        f"  Съедено: {int(today_stats['total_calories'])} ккал\n"
        f"  Приёмов пищи сегодня: {today_stats['meal_count']}\n"
        f"  Всего приёмов за всё время: {total_meals}\n\n"
        f"<b>Регистрация:</b> {user.get('created_at', '—')}"
    )

    await message.reply(text, parse_mode='HTML')


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

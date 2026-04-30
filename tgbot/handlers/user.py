from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from tgbot.models.user import UserModel
from tgbot.models.meal import MealModel
from tgbot.i18n import t_for_user

user_router = Router()


@user_router.message(Command("myid"))
async def get_my_id(message: Message):
    await message.reply(f"Твой Telegram ID: <code>{message.from_user.id}</code>", parse_mode='HTML')


@user_router.message(F.text.in_(["📈 Сегодня", "📈 Bugun"]))
async def show_today_stats(message: Message):
    """Показать статистику за сегодня"""
    user_model = UserModel()
    meal_model = MealModel()

    user = user_model.get_user(message.from_user.id)

    if not user or not user_model.is_onboarding_complete(message.from_user.id):
        await message.answer(t_for_user(message.from_user.id, 'need_onboarding'))
        return

    # Получаем дневную норму
    norm_calories = user.get('daily_calories', 0)
    norm_proteins = user.get('daily_proteins', 0)
    norm_fats = user.get('daily_fats', 0)
    norm_carbs = user.get('daily_carbs', 0)

    # Получаем статистику за день
    stats = meal_model.get_daily_stats(message.from_user.id)

    consumed_calories = int(stats['total_calories'])
    consumed_proteins = round(stats['total_proteins'], 1)
    consumed_fats = round(stats['total_fats'], 1)
    consumed_carbs = round(stats['total_carbs'], 1)

    remaining_calories = norm_calories - consumed_calories
    remaining_proteins = round(norm_proteins - consumed_proteins, 1)
    remaining_fats = round(norm_fats - consumed_fats, 1)
    remaining_carbs = round(norm_carbs - consumed_carbs, 1)

    text = t_for_user(
        message.from_user.id,
        'today_stats',
        norm_calories=norm_calories,
        norm_proteins=norm_proteins,
        norm_fats=norm_fats,
        norm_carbs=norm_carbs,
        consumed_calories=consumed_calories,
        consumed_proteins=consumed_proteins,
        consumed_fats=consumed_fats,
        consumed_carbs=consumed_carbs,
        remaining_calories=remaining_calories,
        remaining_proteins=remaining_proteins,
        remaining_fats=remaining_fats,
        remaining_carbs=remaining_carbs
    )

    await message.answer(text, parse_mode='HTML')

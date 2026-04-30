import logging
from datetime import date
from io import BytesIO

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, BufferedInputFile

from tgbot.misc.states import FoodTrackingStates
from tgbot.models.user import UserModel
from tgbot.models.meal import MealModel
from tgbot.services.food_analyzer import FoodAnalyzer
from tgbot.i18n import t_for_user
from tgbot.keyboards.inline import (
    meal_confirmation_keyboard,
    meal_edit_keyboard,
    portion_keyboard,
    MealActionCallback,
    ProductActionCallback,
    PortionCallback
)

logger = logging.getLogger(__name__)

food_tracking_router = Router()


def format_meal_message(meal: dict, lang: str = "ru") -> str:
    """Форматирует сообщение о приеме пищи"""

    texts = {
        'ru': {
            'title': '🍽 Приём пищи распознан:',
            'total': 'Всего',
            'question': '❓ Добавить этот приём пищи в дневной баланс?',
            'low_confidence': '⚠️ Низкая уверенность в распознавании. Рекомендуем проверить данные.'
        },
        'uz': {
            'title': '🍽 Taom aniqlandi:',
            'total': 'Jami',
            'question': '❓ Bu taomni kunlik balansga qo\'shasizmi?',
            'low_confidence': '⚠️ Aniqlik past. Ma\'lumotlarni tekshiring.'
        }
    }

    t = texts.get(lang, texts['ru'])

    # Заголовок
    lines = [t['title'], '']

    # Продукты
    has_low_confidence = False
    for item in meal['items']:
        confidence = item.get('confidence', 1.0)
        if confidence < 0.5:
            has_low_confidence = True

        lines.append(
            f"• {item['product_name']} — {item['weight']} г\n"
            f"  🔥 {item['calories']} ккал | "
            f"Б: {item['proteins']:.1f} г | "
            f"Ж: {item['fats']:.1f} г | "
            f"У: {item['carbs']:.1f} г"
        )
        lines.append('')

    # Разделитель
    lines.append('━━━━━━━━━━━━')

    # Итого
    lines.append(
        f"🔥 {t['total']}: {meal['total_calories']} ккал\n"
        f"Б: {meal['total_proteins']:.1f} г | "
        f"Ж: {meal['total_fats']:.1f} г | "
        f"У: {meal['total_carbs']:.1f} г"
    )
    lines.append('')

    # Предупреждение о низкой уверенности
    if has_low_confidence:
        lines.append(t['low_confidence'])
        lines.append('')

    # Вопрос
    lines.append(t['question'])

    return '\n'.join(lines)


def format_daily_stats_message(user: dict, stats: dict, lang: str = "ru") -> str:
    """Форматирует сообщение о дневной статистике"""

    texts = {
        'ru': {
            'title': '✅ Приём пищи добавлен',
            'today': '📊 Сегодня:',
            'norm': 'Норма',
            'consumed': 'Съедено',
            'remaining': 'Осталось'
        },
        'uz': {
            'title': '✅ Taom qo\'shildi',
            'today': '📊 Bugun:',
            'norm': 'Norma',
            'consumed': 'Iste\'mol qilindi',
            'remaining': 'Qoldi'
        }
    }

    t = texts.get(lang, texts['ru'])

    # Дневная норма
    daily_calories = user.get('daily_calories', 0)
    daily_proteins = user.get('daily_proteins', 0)
    daily_fats = user.get('daily_fats', 0)
    daily_carbs = user.get('daily_carbs', 0)

    # Съедено
    consumed_calories = int(stats['total_calories'])
    consumed_proteins = round(stats['total_proteins'], 1)
    consumed_fats = round(stats['total_fats'], 1)
    consumed_carbs = round(stats['total_carbs'], 1)

    # Осталось
    remaining_calories = daily_calories - consumed_calories
    remaining_proteins = round(daily_proteins - consumed_proteins, 1)
    remaining_fats = round(daily_fats - consumed_fats, 1)
    remaining_carbs = round(daily_carbs - consumed_carbs, 1)

    lines = [
        t['title'],
        '',
        t['today'],
        f"{t['norm']}: {daily_calories} ккал | Б: {daily_proteins} г | Ж: {daily_fats} г | У: {daily_carbs} г",
        f"{t['consumed']}: {consumed_calories} ккал | Б: {consumed_proteins} г | Ж: {consumed_fats} г | У: {consumed_carbs} г",
        f"{t['remaining']}: {remaining_calories} ккал | Б: {remaining_proteins} г | Ж: {remaining_fats} г | У: {remaining_carbs} г"
    ]

    return '\n'.join(lines)


@food_tracking_router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработчик получения фото еды"""

    # Проверяем, завершен ли онбординг
    user_model = UserModel()
    user = user_model.get_user(message.from_user.id)

    if not user or not user_model.is_onboarding_complete(message.from_user.id):
        await message.answer(t_for_user(message.from_user.id, 'need_onboarding_photo'))
        return

    lang = user.get('language', 'ru')

    try:
        # Отправляем сообщение о начале анализа
        status_msg = await message.answer(t_for_user(message.from_user.id, 'analyzing_photo'))

        # Получаем фото
        photo = message.photo[-1]  # Берем самое большое фото
        file = await bot.get_file(photo.file_id)
        photo_bytes = await bot.download_file(file.file_path)
        photo_data = photo_bytes.read()

        # Анализируем фото
        analyzer = FoodAnalyzer()
        result = analyzer.analyze_food_photo(photo_data)

        # Проверяем успешность анализа
        if not result['success']:
            error_message = result.get('error', '')
            # Если Gemini явно сказал, что это не еда
            if 'не обнаружена еда' in error_message.lower() or 'not food' in error_message.lower():
                await status_msg.edit_text(t_for_user(message.from_user.id, 'no_food_detected'))
            else:
                # Другая ошибка
                await status_msg.edit_text(
                    t_for_user(message.from_user.id, 'analysis_error',
                              error=result.get('error', 'Неизвестная ошибка'))
                )
            return

        # Проверяем, что найдены продукты
        if not result['products'] or len(result['products']) == 0:
            await status_msg.edit_text(t_for_user(message.from_user.id, 'no_food_detected'))
            return

        # Создаем прием пищи
        meal_model = MealModel()
        meal_id = meal_model.create_meal(
            user_id=message.from_user.id,
            photo_file_id=photo.file_id
        )

        # Добавляем продукты
        for product in result['products']:
            meal_model.add_meal_item(
                meal_id=meal_id,
                product_name=product['name'],
                weight=product['weight'],
                calories=product['calories'],
                proteins=product['proteins'],
                fats=product['fats'],
                carbs=product['carbs'],
                confidence=product.get('confidence', 1.0)
            )

        # Получаем созданный прием пищи
        meal = meal_model.get_meal(meal_id)

        # Удаляем сообщение о статусе
        await status_msg.delete()

        # Отправляем результат с кнопками подтверждения
        await message.answer(
            format_meal_message(meal, lang),
            reply_markup=meal_confirmation_keyboard(meal_id, lang)
        )

        # Сохраняем meal_id в состоянии
        await state.update_data(current_meal_id=meal_id)
        await state.set_state(FoodTrackingStates.confirming_meal)

    except Exception as e:
        logger.error(f"Error handling photo: {e}", exc_info=True)
        await message.answer(
            f"❌ Произошла ошибка при обработке фото: {str(e)}\n\n"
            "Попробуйте еще раз."
        )


@food_tracking_router.callback_query(MealActionCallback.filter(F.action == 'confirm'))
async def confirm_meal(callback: CallbackQuery, callback_data: MealActionCallback, state: FSMContext):
    """Показываем выбор размера порции перед подтверждением"""
    await callback.answer()

    meal_model = MealModel()
    user_model = UserModel()

    meal = meal_model.get_meal(callback_data.meal_id)
    if not meal:
        await callback.message.edit_text("❌ Прием пищи не найден.")
        return

    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    texts = {
        'ru': '🍽 В каком количестве вы съели эту еду?',
        'uz': '🍽 Bu taomni qancha miqdorda yedingiz?'
    }

    await callback.message.edit_text(
        texts.get(lang, texts['ru']),
        reply_markup=portion_keyboard(callback_data.meal_id, lang)
    )

    await state.update_data(current_meal_id=callback_data.meal_id)
    await state.set_state(FoodTrackingStates.choosing_portion)


@food_tracking_router.callback_query(PortionCallback.filter())
async def apply_portion(callback: CallbackQuery, callback_data: PortionCallback, state: FSMContext):
    """Применяем множитель порции и подтверждаем приём пищи"""
    await callback.answer()

    multiplier = float(callback_data.multiplier)
    meal_model = MealModel()
    user_model = UserModel()

    meal = meal_model.get_meal(callback_data.meal_id)
    if not meal:
        await callback.message.edit_text("❌ Прием пищи не найден.")
        return

    if multiplier != 1.0:
        for item in meal['items']:
            meal_model.update_meal_item(
                item_id=item['item_id'],
                weight=round(item['weight'] * multiplier),
                calories=round(item['calories'] * multiplier),
                proteins=round(item['proteins'] * multiplier, 1),
                fats=round(item['fats'] * multiplier, 1),
                carbs=round(item['carbs'] * multiplier, 1)
            )

    meal_model.confirm_meal(callback_data.meal_id)

    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    stats = meal_model.get_daily_stats(callback.from_user.id)

    await callback.message.edit_text(
        format_daily_stats_message(user, stats, lang)
    )

    await state.clear()


@food_tracking_router.callback_query(MealActionCallback.filter(F.action == 'edit'))
async def edit_meal(callback: CallbackQuery, callback_data: MealActionCallback, state: FSMContext):
    """Переход к редактированию приема пищи"""
    await callback.answer()

    meal_model = MealModel()
    meal = meal_model.get_meal(callback_data.meal_id)

    if not meal:
        await callback.message.edit_text("❌ Прием пищи не найден.")
        return

    user_model = UserModel()
    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    texts = {
        'ru': '✏️ Выберите продукт для редактирования или удаления:',
        'uz': '✏️ O\'zgartirish yoki o\'chirish uchun mahsulotni tanlang:'
    }

    await callback.message.edit_text(
        texts.get(lang, texts['ru']),
        reply_markup=meal_edit_keyboard(callback_data.meal_id, meal['items'], lang)
    )

    await state.set_state(FoodTrackingStates.editing_product)


@food_tracking_router.callback_query(MealActionCallback.filter(F.action == 'cancel'))
async def cancel_meal(callback: CallbackQuery, callback_data: MealActionCallback, state: FSMContext):
    """Отмена приема пищи"""
    await callback.answer()

    meal_model = MealModel()
    meal_model.cancel_meal(callback_data.meal_id)

    user_model = UserModel()
    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    texts = {
        'ru': '❌ Приём пищи не добавлен',
        'uz': '❌ Taom qo\'shilmadi'
    }

    await callback.message.edit_text(texts.get(lang, texts['ru']))
    await state.clear()


@food_tracking_router.callback_query(MealActionCallback.filter(F.action == 'back_to_confirm'))
async def back_to_confirm(callback: CallbackQuery, callback_data: MealActionCallback, state: FSMContext):
    """Возврат к экрану подтверждения"""
    await callback.answer()

    meal_model = MealModel()
    user_model = UserModel()

    meal = meal_model.get_meal(callback_data.meal_id)
    if not meal:
        await callback.message.edit_text("❌ Прием пищи не найден.")
        return

    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    await callback.message.edit_text(
        format_meal_message(meal, lang),
        reply_markup=meal_confirmation_keyboard(callback_data.meal_id, lang)
    )

    await state.set_state(FoodTrackingStates.confirming_meal)


@food_tracking_router.callback_query(ProductActionCallback.filter(F.action == 'delete'))
async def delete_product(callback: CallbackQuery, callback_data: ProductActionCallback):
    """Удаление продукта из приема пищи"""
    await callback.answer()

    meal_model = MealModel()
    user_model = UserModel()

    # Удаляем продукт
    meal_model.delete_meal_item(callback_data.item_id)

    # Получаем обновленный прием пищи
    meal = meal_model.get_meal(callback_data.meal_id)

    if not meal or not meal['items']:
        # Если продуктов не осталось, удаляем весь прием
        meal_model.cancel_meal(callback_data.meal_id)

        user = user_model.get_user(callback.from_user.id)
        lang = user.get('language', 'ru')

        texts = {
            'ru': '❌ Все продукты удалены. Прием пищи отменен.',
            'uz': '❌ Barcha mahsulotlar o\'chirildi. Taom bekor qilindi.'
        }

        await callback.message.edit_text(texts.get(lang, texts['ru']))
        return

    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    texts = {
        'ru': '✅ Продукт удален.\n\nВыберите продукт для редактирования или удаления:',
        'uz': '✅ Mahsulot o\'chirildi.\n\nO\'zgartirish yoki o\'chirish uchun mahsulotni tanlang:'
    }

    await callback.message.edit_text(
        texts.get(lang, texts['ru']),
        reply_markup=meal_edit_keyboard(callback_data.meal_id, meal['items'], lang)
    )


@food_tracking_router.callback_query(ProductActionCallback.filter(F.action == 'edit_weight'))
async def edit_product_weight(callback: CallbackQuery, callback_data: ProductActionCallback, state: FSMContext):
    """Начало редактирования веса продукта"""
    await callback.answer()

    user_model = UserModel()
    user = user_model.get_user(callback.from_user.id)
    lang = user.get('language', 'ru')

    texts = {
        'ru': '✏️ Введите новый вес продукта в граммах (например: 250):',
        'uz': '✏️ Mahsulotning yangi og\'irligini grammlarda kiriting (masalan: 250):'
    }

    await callback.message.answer(texts.get(lang, texts['ru']))

    # Сохраняем данные в состояние
    await state.update_data(
        editing_item_id=callback_data.item_id,
        editing_meal_id=callback_data.meal_id
    )
    await state.set_state(FoodTrackingStates.editing_weight)


@food_tracking_router.message(FoodTrackingStates.editing_weight)
async def process_new_weight(message: Message, state: FSMContext):
    """Обработка нового веса продукта"""
    try:
        new_weight = int(message.text.strip())

        if new_weight <= 0 or new_weight > 5000:
            await message.answer(t_for_user(message.from_user.id, 'invalid_weight'))
            return

        data = await state.get_data()
        item_id = data['editing_item_id']
        meal_id = data['editing_meal_id']

        meal_model = MealModel()
        user_model = UserModel()

        # Получаем текущий продукт
        meal = meal_model.get_meal(meal_id)
        item = next((i for i in meal['items'] if i['item_id'] == item_id), None)

        if not item:
            await message.answer(t_for_user(message.from_user.id, 'product_not_found'))
            await state.clear()
            return

        # Пересчитываем БЖУ и калории
        old_weight = item['weight']
        ratio = new_weight / old_weight

        new_calories = round(item['calories'] * ratio)
        new_proteins = round(item['proteins'] * ratio, 1)
        new_fats = round(item['fats'] * ratio, 1)
        new_carbs = round(item['carbs'] * ratio, 1)

        # Обновляем продукт
        meal_model.update_meal_item(
            item_id=item_id,
            weight=new_weight,
            calories=new_calories,
            proteins=new_proteins,
            fats=new_fats,
            carbs=new_carbs
        )

        # Получаем обновленный прием пищи
        meal = meal_model.get_meal(meal_id)

        user = user_model.get_user(message.from_user.id)
        lang = user.get('language', 'ru')

        texts = {
            'ru': '✅ Вес обновлен.\n\nВыберите продукт для редактирования или удаления:',
            'uz': '✅ Og\'irlik yangilandi.\n\nO\'zgartirish yoki o\'chirish uchun mahsulotni tanlang:'
        }

        await message.answer(
            texts.get(lang, texts['ru']),
            reply_markup=meal_edit_keyboard(meal_id, meal['items'], lang)
        )

        await state.set_state(FoodTrackingStates.editing_product)

    except ValueError:
        await message.answer(t_for_user(message.from_user.id, 'invalid_number_format'))

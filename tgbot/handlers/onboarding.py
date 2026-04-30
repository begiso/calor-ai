from datetime import date, datetime
from typing import Tuple
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.misc.states import OnboardingStates
from tgbot.keyboards.reply import main_menu_keyboard
from tgbot.i18n import t_for_user, t, clear_lang_cache
from tgbot.keyboards.inline import (
    language_inline_keyboard,
    gender_inline_keyboard,
    activity_inline_keyboard,
)
from tgbot.models.user import UserModel
from tgbot.services.calculations import BodyAnalysisCalculator, NutritionCalculator

onboarding_router = Router()


def validate_age(birth_date: date, user_id: int) -> Tuple[bool, str]:
    """Валидация возраста: 14-80 лет"""
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    if age < 14:
        return False, t_for_user(user_id, 'age_too_young')
    if age > 80:
        return False, t_for_user(user_id, 'age_too_old')
    return True, ""


def validate_height(height: int, user_id: int) -> Tuple[bool, str]:
    """Валидация роста: 120-230 см"""
    if height < 120:
        return False, t_for_user(user_id, 'height_too_short')
    if height > 230:
        return False, t_for_user(user_id, 'height_too_tall')
    return True, ""


def validate_weight(weight: float, user_id: int) -> Tuple[bool, str]:
    """Валидация веса: 40-250 кг"""
    if weight < 40:
        return False, t_for_user(user_id, 'weight_too_low')
    if weight > 250:
        return False, t_for_user(user_id, 'weight_too_high')
    return True, ""


def parse_activity_level(text: str):
    """Парсинг уровня активности из текста (поддержка русского и узбекского)"""
    text_lower = text.lower()
    # Поддержка обоих языков для каждого уровня
    if "0" in text_lower and ("mashq" in text_lower or "тренировок" in text_lower or "ноль" in text_lower):
        return 0
    elif "1-2" in text_lower and ("mashq" in text_lower or "тренировки" in text_lower):
        return 1
    elif "3-4" in text_lower and ("mashq" in text_lower or "тренировки" in text_lower):
        return 3
    elif ("5+" in text_lower or "пять" in text_lower) and ("mashq" in text_lower or "тренировок" in text_lower):
        return 5
    # Если не совпало с полным текстом, пробуем по числу
    elif "0" in text_lower:
        return 0
    elif "1-2" in text_lower or "1" in text_lower or "2" in text_lower:
        return 1
    elif "3-4" in text_lower or "3" in text_lower or "4" in text_lower:
        return 3
    elif "5" in text_lower:
        return 5
    return None


@onboarding_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext, config):
    """Обработчик команды /start"""
    user_model = UserModel()
    user = user_model.get_user(message.from_user.id)

    # Если онбординг завершен, показываем главное меню
    if user and user_model.is_onboarding_complete(message.from_user.id):
        await message.answer(
            "Добро пожаловать обратно! 👋\n\n"
            + t_for_user(message.from_user.id, 'choose_action'),
            reply_markup=main_menu_keyboard(UserModel().get_user(message.from_user.id).get('language', 'ru'))
        )
        return

    # Получаем имя пользователя
    username = message.from_user.first_name or message.from_user.username or "друг"

    # Если это новый пользователь, уведомляем админа
    if not user:
        # Уведомляем всех админов о новом пользователе
        for admin_id in config.tg_bot.admin_ids:
            try:
                notification = t('ru', 'new_user_joined',
                               username=message.from_user.full_name or message.from_user.username or "Unknown",
                               user_id=message.from_user.id,
                               language="не выбран")
                await message.bot.send_message(admin_id, notification, parse_mode='HTML')
            except Exception:
                # Игнорируем ошибки отправки (админ мог заблокировать бота)
                pass

    # Начинаем онбординг
    await state.set_state(OnboardingStates.language)
    await message.answer(
        t('ru', 'start_welcome', username=username),
        reply_markup=language_inline_keyboard()
    )


@onboarding_router.message(OnboardingStates.language)
async def process_language(message: Message, state: FSMContext):
    """Обработка выбора языка"""
    text = message.text.lower()
    
    if "русск" in text or "ru" in text:
        language = "ru"
    elif "o'zbek" in text or "uzbek" in text or "узбек" in text or "uz" in text:
        language = "uz"
    else:
        await message.answer(t_for_user(message.from_user.id, 'choose_language_prompt'))
        return
    
    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, language=language)
    
    await state.update_data(language=language)
    await state.set_state(OnboardingStates.gender)
    await message.answer(
        t(language, 'choose_gender'),
        reply_markup=gender_inline_keyboard()
    )


@onboarding_router.message(OnboardingStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Обработка выбора пола"""
    text = message.text.lower()
    
    if "мужчин" in text or "male" in text or "erkak" in text:
        gender = "male"
    elif "женщин" in text or "female" in text or "ayol" in text:
        gender = "female"
    else:
        await message.answer(t_for_user(message.from_user.id, 'choose_from_options'))
        return
    
    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, gender=gender)
    
    await state.update_data(gender=gender)
    await state.set_state(OnboardingStates.birth_date)
    await message.answer(t_for_user(message.from_user.id, 'birth_date_prompt'))


@onboarding_router.message(OnboardingStates.birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    """Обработка даты рождения"""
    try:
        birth_date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
    except ValueError:
        await message.answer(t_for_user(message.from_user.id, 'invalid_format_date'))
        return
    
    is_valid, error_msg = validate_age(birth_date, message.from_user.id)
    if not is_valid:
        await message.answer(error_msg + "\n" + t_for_user(message.from_user.id, 'birth_date_prompt'))
        return

    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, birth_date=birth_date)

    await state.update_data(birth_date=birth_date)
    await state.set_state(OnboardingStates.height)
    await message.answer(t_for_user(message.from_user.id, 'height_prompt'))


@onboarding_router.message(OnboardingStates.height)
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    try:
        height = int(message.text.strip())
    except ValueError:
        await message.answer(t_for_user(message.from_user.id, 'enter_number_example', example=175))
        return
    
    is_valid, error_msg = validate_height(height, message.from_user.id)
    if not is_valid:
        await message.answer(error_msg + "\n" + t_for_user(message.from_user.id, 'enter_number_example', example=175))
        return

    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, height=height)

    await state.update_data(height=height)
    await state.set_state(OnboardingStates.weight)
    await message.answer(t_for_user(message.from_user.id, 'weight_prompt'))


@onboarding_router.message(OnboardingStates.weight)
async def process_weight(message: Message, state: FSMContext):
    """Обработка веса"""
    try:
        weight = float(message.text.strip().replace(",", "."))
    except ValueError:
        await message.answer(t_for_user(message.from_user.id, 'enter_number_example', example='75.5'))
        return
    
    is_valid, error_msg = validate_weight(weight, message.from_user.id)
    if not is_valid:
        await message.answer(error_msg + "\n" + t_for_user(message.from_user.id, 'enter_number_example', example='75.5'))
        return
    
    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, weight=weight)
    
    await state.update_data(weight=weight)
    await state.set_state(OnboardingStates.activity_level)
    lang = UserModel().get_user(message.from_user.id).get('language', 'ru')
    await message.answer(
        t_for_user(message.from_user.id, 'activity_prompt'),
        reply_markup=activity_inline_keyboard(lang=lang)
    )


@onboarding_router.message(OnboardingStates.activity_level)
async def process_activity_level(message: Message, state: FSMContext):
    """Обработка уровня активности"""
    activity_level = parse_activity_level(message.text)
    
    if activity_level is None:
        await message.answer(t_for_user(message.from_user.id, 'choose_from_options'))
        return
    
    user_model = UserModel()
    user_model.create_or_update_user(message.from_user.id, activity_level=activity_level)
    
    # Получаем все данные пользователя
    user = user_model.get_user(message.from_user.id)
    
    # Рассчитываем результаты
    body_calc = BodyAnalysisCalculator()
    nutrition_calc = NutritionCalculator()
    
    body_data = body_calc.calculate_all(
        gender=user['gender'],
        birth_date=date.fromisoformat(user['birth_date']),
        height=user['height'],
        weight=user['weight']
    )
    
    nutrition_data = nutrition_calc.calculate_all(
        gender=user['gender'],
        birth_date=date.fromisoformat(user['birth_date']),
        height=user['height'],
        weight=user['weight'],
        activity_level=user['activity_level'],
        target_weight=body_data['target_weight'],
        excess_fat_kg=body_data['excess_fat']
    )
    
    # Сохраняем результаты в состояние (для отображения)
    await state.update_data(
        activity_level=activity_level,
        body_data=body_data,
        nutrition_data=nutrition_data
    )

    # Сохраняем дневную норму в базе данных
    user_model.create_or_update_user(
        message.from_user.id,
        daily_calories=nutrition_data['calories'],
        daily_proteins=nutrition_data['proteins'],
        daily_fats=nutrition_data['fats'],
        daily_carbs=nutrition_data['carbs']
    )

    await state.clear()
    
    # Показываем финальное сообщение в локализованном формате
    excess_fat = body_data['excess_fat']
    weight_loss_info = nutrition_data['weight_loss_time']

    # Выбираем правильное сообщение в зависимости от наличия лишнего веса
    if excess_fat > 0:
        # Есть лишний вес - показываем норму для похудения
        extra = ""
        if weight_loss_info['display_text']:
            extra = "\n\n" + weight_loss_info['display_text']

        text = t_for_user(message.from_user.id, 'onboarding_results_with_excess',
                          excess_fat=excess_fat,
                          calories=nutrition_data['calories'],
                          carbs=nutrition_data['carbs'],
                          proteins=nutrition_data['proteins'],
                          fats=nutrition_data['fats'],
                          extra=extra)
    else:
        # Нет лишнего веса - показываем норму для поддержания
        text = t_for_user(message.from_user.id, 'onboarding_results_no_excess',
                          calories=nutrition_data['calories'],
                          carbs=nutrition_data['carbs'],
                          proteins=nutrition_data['proteins'],
                          fats=nutrition_data['fats'])

    await message.answer(text)

    # Показываем инструкцию как использовать бота
    await message.answer(t_for_user(message.from_user.id, 'onboarding_complete'))

    # Показываем главное меню
    user_lang = UserModel().get_user(message.from_user.id).get('language', 'ru')
    await message.answer(
        "\n" + t_for_user(message.from_user.id, 'choose_action'),
        reply_markup=main_menu_keyboard(user_lang)
    )



@onboarding_router.callback_query(F.data.startswith("lang:"))
async def process_language_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора языка через inline-кнопку"""
    await callback.answer()
    _, lang = callback.data.split(":", 1)
    if lang not in ("ru", "uz"):
        await callback.message.answer(t_for_user(callback.from_user.id, 'invalid_choice'))
        return

    user_model = UserModel()
    user_model.create_or_update_user(callback.from_user.id, language=lang)

    # Очищаем кэш языка для этого пользователя
    clear_lang_cache()

    # If user is in the language state during onboarding, proceed to gender step
    current_state = await state.get_state()
    if current_state and "language" in current_state:
        await state.update_data(language=lang)
        await state.set_state(OnboardingStates.gender)
        await callback.message.answer(
            t(lang, 'choose_gender'),
            reply_markup=gender_inline_keyboard(lang=lang)
        )
    else:
        # Language change requested from menu — just confirm change
        lang_text = "Русский" if lang == "ru" else "O'zbek"
        await callback.message.answer(t(lang, 'language_changed', lang_text=lang_text))
        # Update shown main menu to new language
        await callback.message.answer("\n" + t(lang, 'choose_action'), reply_markup=main_menu_keyboard(lang))


@onboarding_router.callback_query(F.data.startswith("gender:"))
async def process_gender_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора пола через inline-кнопку"""
    await callback.answer()
    _, gender = callback.data.split(":", 1)
    if gender not in ("male", "female"):
        await callback.message.answer(t_for_user(callback.from_user.id, 'invalid_choice'))
        return

    user_model = UserModel()
    user_model.create_or_update_user(callback.from_user.id, gender=gender)

    await state.update_data(gender=gender)
    await state.set_state(OnboardingStates.birth_date)
    await callback.message.answer(t_for_user(callback.from_user.id, 'birth_date_prompt'))


@onboarding_router.callback_query(F.data.startswith("activity:"))
async def process_activity_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора уровня активности через inline-кнопку"""
    await callback.answer()
    _, activity_str = callback.data.split(":", 1)
    try:
        activity_level = int(activity_str)
    except ValueError:
        await callback.message.answer(t_for_user(callback.from_user.id, 'invalid_choice_again'))
        return

    user_model = UserModel()
    user_model.create_or_update_user(callback.from_user.id, activity_level=activity_level)

    # Получаем все данные пользователя
    user = user_model.get_user(callback.from_user.id)

    # Рассчитываем результаты
    body_calc = BodyAnalysisCalculator()
    nutrition_calc = NutritionCalculator()

    body_data = body_calc.calculate_all(
        gender=user['gender'],
        birth_date=date.fromisoformat(user['birth_date']),
        height=user['height'],
        weight=user['weight']
    )

    nutrition_data = nutrition_calc.calculate_all(
        gender=user['gender'],
        birth_date=date.fromisoformat(user['birth_date']),
        height=user['height'],
        weight=user['weight'],
        activity_level=user['activity_level'],
        target_weight=body_data['target_weight'],
        excess_fat_kg=body_data['excess_fat']
    )

    # Сохраняем результаты в состояние (для отображения)
    await state.update_data(
        activity_level=activity_level,
        body_data=body_data,
        nutrition_data=nutrition_data
    )

    # Сохраняем дневную норму в базе данных
    user_model.create_or_update_user(
        callback.from_user.id,
        daily_calories=nutrition_data['calories'],
        daily_proteins=nutrition_data['proteins'],
        daily_fats=nutrition_data['fats'],
        daily_carbs=nutrition_data['carbs']
    )

    await state.clear()

    # Показываем финальное сообщение в локализованном формате
    excess_fat = body_data['excess_fat']
    weight_loss_info = nutrition_data['weight_loss_time']

    # Выбираем правильное сообщение в зависимости от наличия лишнего веса
    if excess_fat > 0:
        # Есть лишний вес - показываем норму для похудения
        extra = ""
        if weight_loss_info['display_text']:
            extra = "\n\n" + weight_loss_info['display_text']

        text = t_for_user(callback.from_user.id, 'onboarding_results_with_excess',
                          excess_fat=excess_fat,
                          calories=nutrition_data['calories'],
                          carbs=nutrition_data['carbs'],
                          proteins=nutrition_data['proteins'],
                          fats=nutrition_data['fats'],
                          extra=extra)
    else:
        # Нет лишнего веса - показываем норму для поддержания
        text = t_for_user(callback.from_user.id, 'onboarding_results_no_excess',
                          calories=nutrition_data['calories'],
                          carbs=nutrition_data['carbs'],
                          proteins=nutrition_data['proteins'],
                          fats=nutrition_data['fats'])

    await callback.message.answer(text)

    # Показываем инструкцию как использовать бота
    await callback.message.answer(t_for_user(callback.from_user.id, 'onboarding_complete'))

    # Показываем главное меню (reply keyboard) на языке пользователя
    user_lang = UserModel().get_user(callback.from_user.id).get('language', 'ru')
    await callback.message.answer(
        "\n" + t_for_user(callback.from_user.id, 'choose_action'),
        reply_markup=main_menu_keyboard(user_lang)
    )


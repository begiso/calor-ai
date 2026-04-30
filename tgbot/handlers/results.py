from datetime import date
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.keyboards.reply import main_menu_keyboard
from tgbot.keyboards.inline import recalc_inline_keyboard, language_inline_keyboard, recalc_confirm_keyboard, gender_inline_keyboard
from tgbot.models.user import UserModel
from tgbot.i18n import t_for_user, t
from tgbot.services.calculations import BodyAnalysisCalculator, NutritionCalculator

results_router = Router()


@results_router.message(F.text.in_(["📊 Анализ тела", "📊 Tana tahlili"]))
async def show_body_analysis_handler(message: Message):
    """Обработчик для отображения анализа тела"""
    user_model = UserModel()
    user = user_model.get_user(message.from_user.id)
    
    if not user or not user_model.is_onboarding_complete(message.from_user.id):
        await message.answer(
            t_for_user(message.from_user.id, 'need_onboarding')
        )
        return
    
    body_calc = BodyAnalysisCalculator()
    body_data = body_calc.calculate_all(
        gender=user['gender'],
        birth_date=date.fromisoformat(user['birth_date']),
        height=user['height'],
        weight=user['weight']
    )
    
    lang = user.get('language', 'ru')
    activity_label = t(lang, f"activity_{user.get('activity_level', 0)}")

    title = t_for_user(message.from_user.id, 'analysis_title')
    body = t_for_user(
        message.from_user.id,
        'analysis_body',
        height=user['height'],
        weight=user['weight'],
        activity=activity_label,
        age=body_data['age'],
        bmi=body_data['bmi'],
        body_fat_percentage=body_data['body_fat_percentage'],
        lean_body_mass=body_data['lean_body_mass'],
        excess_fat=body_data['excess_fat'],
    )

    # Attach localized inline "Пересчитать" button under the analysis text
    await message.answer(f"{title}\n\n{body}", parse_mode='HTML', reply_markup=recalc_inline_keyboard(lang=lang))



# Note: main menu uses reply keyboard. Message handlers already cover reply button presses.


@results_router.message(F.text.in_(["🍎 Ежедневная норма", "🍎 Kunlik norma"]))
async def show_daily_norm_handler(message: Message):
    """Обработчик для отображения ежедневной нормы"""
    user_model = UserModel()
    user = user_model.get_user(message.from_user.id)
    
    if not user or not user_model.is_onboarding_complete(message.from_user.id):
        await message.answer(
            t_for_user(message.from_user.id, 'need_onboarding')
        )
        return
    
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
    
    title = t_for_user(message.from_user.id, 'daily_norm_title')
    body = t_for_user(
        message.from_user.id,
        'daily_norm_body',
        calories=nutrition_data['calories'],
        proteins=nutrition_data['proteins'],
        fats=nutrition_data['fats'],
        carbs=nutrition_data['carbs'],
    )

    text = f"{title}\n\n{body}\n\n<i>{t_for_user(message.from_user.id, 'norm_calculated_for_weight_loss')}</i>"

    weight_loss_info = nutrition_data['weight_loss_time']
    if weight_loss_info['display_text']:
        text += f"\n\n{weight_loss_info['display_text']}"

    await message.answer(text, parse_mode='HTML')


@results_router.message(F.text.in_(["🌐 Язык", "🌐 Til"]))
async def change_language_menu(message: Message):
    """Отображает inline-кнопки для смены языка из меню"""
    await message.answer(t_for_user(message.from_user.id, 'choose_language'), reply_markup=language_inline_keyboard())



@results_router.callback_query(F.data == "recalc")
async def recalc_callback(callback: CallbackQuery, state: FSMContext):
    """Callback for inline 'Пересчитать' under analysis message: restart onboarding."""
    # Ask for confirmation before resetting user data
    await callback.answer()
    lang = UserModel().get_user(callback.from_user.id).get('language', 'ru')
    await callback.message.answer(
        t_for_user(callback.from_user.id, 'recalc_confirm'),
        reply_markup=recalc_confirm_keyboard(lang=lang)
    )


@results_router.callback_query(F.data == "recalc_confirm:no")
async def recalc_cancel(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(t_for_user(callback.from_user.id, 'recalc_cancel'))


@results_router.callback_query(F.data == "recalc_confirm:yes")
async def recalc_confirm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    user_model = UserModel()
    user_model.reset_onboarding(callback.from_user.id)
    await state.clear()

    from tgbot.misc.states import OnboardingStates

    # Start onboarding but skip language selection (we're not changing language here)
    await state.set_state(OnboardingStates.gender)

    # Short localized message and prompt for gender
    lang = UserModel().get_user(callback.from_user.id).get('language', 'ru')
    await callback.message.answer(t_for_user(callback.from_user.id, 'recalc_proceed'))
    await callback.message.answer(t(lang, 'choose_gender'), reply_markup=gender_inline_keyboard(lang=lang))



# Removed menu callback handlers because main menu uses reply keyboard buttons handled by message handlers.


@results_router.message(F.text == "🔄 Пересчитать")
async def recalculate_handler(message: Message, state: FSMContext):
    """Обработчик для пересчета (запускает онбординг заново)"""
    user_model = UserModel()
    
    # Сбрасываем данные онбординга
    user_model.reset_onboarding(message.from_user.id)
    
    # Очищаем состояние FSM
    await state.clear()
    
    # Запускаем онбординг заново
    from tgbot.misc.states import OnboardingStates
    from tgbot.keyboards.reply import language_keyboard
    
    await state.set_state(OnboardingStates.language)
    
    # Получаем имя пользователя
    username = message.from_user.first_name or message.from_user.username or "друг"
    
    await message.answer(
        f"Привет, {username}! 👋\n\n"
        "Я calorAI — бот для расчета калорий и БЖУ.\n\n"
        "Помогу понять:\n"
        "• Есть ли у вас лишний жир\n"
        "• Сколько калорий нужно для похудения\n"
        "• Какие белки, жиры и углеводы потреблять\n\n"
        "Давайте обновим ваши данные. Выберите язык:",
        reply_markup=language_keyboard()
    )


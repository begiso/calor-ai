from typing import Dict
from functools import lru_cache

from tgbot.models.user import UserModel


MESSAGES: Dict[str, Dict[str, str]] = {
    # Start / onboarding
    "start_welcome": {
        "ru": "Привет, {username}! 👋\n\nЯ calorAI — бот для расчета калорий и БЖУ.\n\nПомогу понять:\n• Есть ли у вас лишний жир\n• Сколько калорий нужно для похудения\n• Какие белки, жиры и углеводы потреблять\n\nВыберите язык:",
        "uz": "Salom, {username}! 👋\n\nMen calorAI — kaloriya va BJU hisoblovchi botman.\n\nYordam beraman:\n• Tanadagi yog'ni aniqlash\n• Qancha kaloriyaga ehtiyoj bor\n• Qaysi oqsillar, yog'lar va uglevodlarni iste'mol qilish\n\nTilni tanlang:"
    },
    "choose_gender": {
        "ru": "Отлично! Теперь укажите ваш пол:",
        "uz": "Ajoyib! Endi jinsingizni ko'rsating:"
    },
    "birth_date_prompt": {
        "ru": "Укажите вашу дату рождения в формате ДД.ММ.ГГГГ\nНапример: 15.05.1990",
        "uz": "Tug'ilgan sanangizni DD.MM.YYYY formatida kiriting\nMasalan: 15.05.1990"
    },
    "height_prompt": {
        "ru": "Укажите ваш рост в сантиметрах (например: 175)",
        "uz": "Bo'yingizni santimetrda kiriting (masalan: 175)"
    },
    "weight_prompt": {
        "ru": "Укажите ваш вес в килограммах (например: 75.5)",
        "uz": "Vazningizni kilogrammlarda kiriting (masalan: 75.5)"
    },
    "activity_prompt": {
        "ru": "Сколько тренировок в неделю вы делаете?",
        "uz": "Haftada necha marta mashq qilasiz?"
    },
    # Recalc
    "recalc_confirm": {
        "ru": "Вы уверены, что хотите изменить данные?",
        "uz": "Ma'lumotlarni o'zgartirmoqchimisiz?"
    },
    "recalc_label": {"ru": "🔄 Пересчитать", "uz": "🔄 Yangilash"},
    "recalc_yes": {"ru": "✅ Да, изменить", "uz": "✅ Ha, o'zgartirish"},
    "recalc_no": {"ru": "❌ Нет, оставить", "uz": "❌ Yo'q, qoldirish"},
    "recalc_cancel": {
        "ru": "Окей, данные не изменены.",
        "uz": "Xo'p, ma'lumotlar o'zgarmadi."
    },
    "recalc_proceed": {
        "ru": "Давайте обновим ваши данные",
        "uz": "Keling, ma'lumotlaringizni yangilaymiz"
    },
    "enter_number_example": {
        "ru": "Пожалуйста, введите число (например: {example}):",
        "uz": "Iltimos, son kiriting (masalan: {example}):"
    },
    "invalid_format_date": {
        "ru": "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\nНапример: 15.05.1990",
        "uz": "Noto'g'ri sana formati. Iltimos, sanani DD.MM.YYYY formatida kiriting\nMasalan: 15.05.1990"
    },
    "choose_from_options": {"ru": "Пожалуйста, выберите вариант из предложенных:", "uz": "Iltimos, taklif qilingan variantlardan tanlang:"},
    "language_changed": {
        "ru": "Язык успешно изменён на {lang_text}",
        "uz": "Til muvaffaqiyatli {lang_text} ga o'zgartirildi"
    },
    "choose_language": {"ru": "Выберите язык:", "uz": "Tilni tanlang:"},
    "choose_action": {"ru": "Выберите действие:", "uz": "Harakatni tanlang:"},
    "need_onboarding": {"ru": "Для начала пройдите онбординг. Отправьте /start", "uz": "Avvalo onboardingdan o'ting. /start yuboring"},
    # Results
    "analysis_title": {
        "ru": "📊 <b>Анализ тела</b>",
        "uz": "📊 <b>Tana tahlili</b>"
    },
    "analysis_body": {
        "ru": "Рост: {height} см\nВес: {weight} кг\nТренировок в неделю: {activity}\nВозраст: {age} лет\nИМТ: {bmi} (справочно)\nПроцент жира: {body_fat_percentage}%\nБезжировая масса: {lean_body_mass} кг\nРеальный лишний жир: {excess_fat} кг",
        "uz": "Bo'y: {height} sm\nVazn: {weight} kg\nHaftalik mashqlar: {activity}\nYosh: {age} yosh\nBMI: {bmi} (ma'lumot uchun)\nTana yog'i foizi: {body_fat_percentage}%\nMushaklarsiz massa: {lean_body_mass} kg\nKeraksiz yog': {excess_fat} kg"
    },
    "daily_norm_title": {
        "ru": "🍎 <b>Ежедневная норма</b>",
        "uz": "🍎 <b>Kunlik norma</b>"
    },
    "daily_norm_body": {
        "ru": "Калории: {calories} ккал\nБелки: {proteins} г\nЖиры: {fats} г\nУглеводы: {carbs} г",
        "uz": "Kaloriyalar: {calories} kkal\nOqsillar: {proteins} g\nYog'lar: {fats} g\nUglevodlar: {carbs} g"
    },
    "onboarding_results_with_excess": {
        "ru": "У вас {excess_fat} кг лишнего веса. Ваша норма для похудения:\n\n🔥 Калории: {calories} ккал\n🍞 Углеводы: {carbs} г\n🥩 Белки: {proteins} г\n🥑 Жиры: {fats} г{extra}",
        "uz": "Sizda {excess_fat} kg ortiqcha vazn bor. Ozish uchun kunlik norma:\n\n🔥 Kaloriya: {calories} kkal\n🍞 Uglevod: {carbs} g\n🥩 Oqsil: {proteins} g\n🥑 Yog': {fats} g{extra}"
    },
    "onboarding_results_no_excess": {
        "ru": "У вас отличная форма! 💪\nВаш текущий вес близок к оптимальному.\n\nВаша норма для поддержания веса:\n\n🔥 Калории: {calories} ккал\n🍞 Углеводы: {carbs} г\n🥩 Белки: {proteins} г\n🥑 Жиры: {fats} г",
        "uz": "Sizning vazningiz juda yaxshi! 💪\nHozirgi vazningiz optimal darajada.\n\nVaznni saqlash uchun kunlik norma:\n\n🔥 Kaloriya: {calories} kkal\n🍞 Uglevod: {carbs} g\n🥩 Oqsil: {proteins} g\n🥑 Yog': {fats} g"
    },
    # Menu labels
    "menu_analysis": {"ru": "📊 Анализ тела", "uz": "📊 Tana tahlili"},
    "menu_norm": {"ru": "🍎 Ежедневная норма", "uz": "🍎 Kunlik norma"},
    "menu_today": {"ru": "📈 Сегодня", "uz": "📈 Bugun"},
    "menu_language": {"ru": "🌐 Язык", "uz": "🌐 Til"},
    # Today's stats
    "today_stats": {
        "ru": "📈 <b>Сегодня</b>\n\n<b>Норма:</b>\nКалории: {norm_calories} ккал\nБелки: {norm_proteins} г\nЖиры: {norm_fats} г\nУглеводы: {norm_carbs} г\n\n<b>Съедено:</b>\nКалории: {consumed_calories} ккал\nБелки: {consumed_proteins} г\nЖиры: {consumed_fats} г\nУглеводы: {consumed_carbs} г\n\n<b>Осталось:</b>\nКалории: {remaining_calories} ккал\nБелки: {remaining_proteins} г\nЖиры: {remaining_fats} г\nУглеводы: {remaining_carbs} г",
        "uz": "<b>Bugun</b>\n\n<b>Norma:</b>\nKaloriya: {norm_calories} kkal\nOqsillar: {norm_proteins} g\nYog'lar: {norm_fats} g\nUglevodlar: {norm_carbs} g\n\n<b>Iste'mol qilindi:</b>\nKaloriya: {consumed_calories} kkal\nOqsillar: {consumed_proteins} g\nYog'lar: {consumed_fats} g\nUglevodlar: {consumed_carbs} g\n\n<b>Qoldi:</b>\nKaloriya: {remaining_calories} kkal\nOqsillar: {remaining_proteins} g\nYog'lar: {remaining_fats} g\nUglevodlar: {remaining_carbs} g"
    },
    "activity_0": {"ru": "0 тренировок", "uz": "0 mashq"},
    "activity_1": {"ru": "1-2 тренировки", "uz": "1-2 mashq"},
    "activity_3": {"ru": "3-4 тренировки", "uz": "3-4 mashq"},
    "activity_5": {"ru": "5+ тренировок", "uz": "5+ mashq"},
    "gender_male": {"ru": "👨 Мужчина", "uz": "👨 Erkak"},
    "gender_female": {"ru": "👩 Женщина", "uz": "👩 Ayol"},
    # Validation errors
    "age_too_young": {"ru": "Возраст должен быть не менее 14 лет", "uz": "Yosh 14 yoshdan kam bo'lmasligi kerak"},
    "age_too_old": {"ru": "Возраст должен быть не более 80 лет", "uz": "Yosh 80 yoshdan oshmasligi kerak"},
    "height_too_short": {"ru": "Рост должен быть не менее 120 см", "uz": "Bo'y 120 sm dan kam bo'lmasligi kerak"},
    "height_too_tall": {"ru": "Рост должен быть не более 230 см", "uz": "Bo'y 230 sm dan oshmasligi kerak"},
    "weight_too_low": {"ru": "Вес должен быть не менее 40 кг", "uz": "Vazn 40 kg dan kam bo'lmasligi kerak"},
    "weight_too_high": {"ru": "Вес должен быть не более 250 кг", "uz": "Vazn 250 kg dan oshmasligi kerak"},
    "invalid_choice": {"ru": "Неверный выбор. Попробуйте снова.", "uz": "Noto'g'ri tanlov. Qaytadan urinib ko'ring."},
    "invalid_choice_again": {"ru": "Неверный выбор. Пожалуйста, выберите снова.", "uz": "Noto'g'ri tanlov. Iltimos, qaytadan tanlang."},
    # Food tracking
    "need_onboarding_photo": {"ru": "Пожалуйста, сначала завершите регистрацию. Используйте /start", "uz": "Iltimos, avval ro'yxatdan o'ting. /start buyrug'ini yuboring"},
    "analyzing_photo": {"ru": "🔍 Анализирую фото...", "uz": "🔍 Suratni tahlil qilyapman..."},
    "analysis_error": {"ru": "❌ Ошибка анализа: {error}\n\nПопробуйте отправить другое фото.", "uz": "❌ Tahlil xatosi: {error}\n\nBoshqa rasm yuboring."},
    "no_food_detected": {
        "ru": "🤔 На фото не обнаружена еда или напитки.\n\n📸 Пожалуйста, отправьте фото:\n• Готовых блюд\n• Продуктов питания\n• Напитков\n• Снеков и закусок\n\nУбедитесь, что фото четкое и еда хорошо видна!",
        "uz": "🤔 Rasmda taom yoki ichimlik aniqlanmadi.\n\n📸 Iltimos, rasm yuboring:\n• Tayyor taomlar\n• Oziq-ovqat mahsulotlari\n• Ichimliklar\n• Gazaklar\n\nRasm aniq va taom yaxshi ko'rinishi kerak!"
    },
    "choose_language_prompt": {"ru": "Пожалуйста, выберите язык из предложенных вариантов:", "uz": "Iltimos, taklif etilgan variantlardan tilni tanlang:"},
    "onboarding_complete": {
        "ru": "🎉 Отлично! Регистрация завершена.\n\n📸 Теперь вы можете отправить мне фото вашей еды, и я:\n• Распознаю продукты\n• Подсчитаю калории и БЖУ\n• Вычту из вашей дневной нормы\n• Покажу, сколько калорий осталось\n\nПросто отправьте фото еды! 🍽",
        "uz": "🎉 Ajoyib! Ro'yxatdan o'tish tugallandi.\n\n📸 Endi menga taomingiz rasmini yuborishingiz mumkin, men:\n• Mahsulotlarni aniqlayman\n• Kaloriya va BJU hisoblayman\n• Kunlik normangizdan ayiraman\n• Qancha kaloriya qolganini ko'rsataman\n\nFaqat taom rasmini yuboring! 🍽"
    },
    "norm_calculated_for_weight_loss": {
        "ru": "Эта норма рассчитана для снижения веса без потери мышц.",
        "uz": "Bu norma mushaklar yo'qotilmagan holda vazn kamayishi uchun hisoblab chiqilgan."
    },
    # Food tracking errors
    "invalid_weight": {
        "ru": "❌ Неверный вес. Введите значение от 1 до 5000 грамм.",
        "uz": "❌ Noto'g'ri og'irlik. 1 dan 5000 grammgacha qiymat kiriting."
    },
    "product_not_found": {
        "ru": "❌ Продукт не найден.",
        "uz": "❌ Mahsulot topilmadi."
    },
    "invalid_number_format": {
        "ru": "❌ Неверный формат. Введите число (например: 250)",
        "uz": "❌ Noto'g'ri format. Son kiriting (masalan: 250)"
    },
    # Admin messages
    "new_user_joined": {
        "ru": "👤 Новый пользователь!\n\n<b>Имя:</b> {username}\n<b>ID:</b> <code>{user_id}</code>\n<b>Язык:</b> {language}",
        "uz": "👤 Yangi foydalanuvchi!\n\n<b>Ism:</b> {username}\n<b>ID:</b> <code>{user_id}</code>\n<b>Til:</b> {language}"
    },
    "stats_title": {
        "ru": "📊 <b>Статистика бота</b>",
        "uz": "📊 <b>Bot statistikasi</b>"
    },
}


@lru_cache(maxsize=1000)
def get_lang(user_id: int) -> str:
    """Получить язык пользователя с кэшированием"""
    user = UserModel().get_user(user_id)
    return (user or {}).get("language", "ru")


def clear_lang_cache():
    """Очистить кэш языков (вызывать при изменении языка пользователя)"""
    get_lang.cache_clear()


def t_for_user(user_id: int, key: str, **kwargs) -> str:
    """Получить перевод для пользователя"""
    lang = get_lang(user_id)
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("ru", "")).format(**kwargs)


def t(lang: str, key: str, **kwargs) -> str:
    """Получить перевод для конкретного языка"""
    return MESSAGES.get(key, {}).get(lang, MESSAGES.get(key, {}).get("ru", "")).format(**kwargs)

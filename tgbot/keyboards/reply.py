from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def language_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора языка"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text="🇺🇿 O'zbek")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def gender_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Клавиатура выбора пола (поддержка русского и узбекского)"""
    from tgbot.i18n import t
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "gender_male"))],
            [KeyboardButton(text=t(lang, "gender_female"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def activity_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Клавиатура выбора уровня активности (поддержка русского и узбекского)"""
    from tgbot.i18n import t
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(lang, "activity_0"))],
            [KeyboardButton(text=t(lang, "activity_1"))],
            [KeyboardButton(text=t(lang, "activity_3"))],
            [KeyboardButton(text=t(lang, "activity_5"))],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def main_menu_keyboard(lang: str = "ru") -> ReplyKeyboardMarkup:
    """Главное меню после завершения онбординга"""
    from tgbot.i18n import t
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t(lang, "menu_analysis")),
                KeyboardButton(text=t(lang, "menu_norm")),
            ],
            [
                KeyboardButton(text=t(lang, "menu_today")),
                KeyboardButton(text=t(lang, "menu_language")),
            ],
        ],
        resize_keyboard=True
    )
    return keyboard


def skip_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой пропуска (для будущего использования)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏭ Пропустить")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


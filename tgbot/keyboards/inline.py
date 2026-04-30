from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# This is a simple keyboard, that contains 2 buttons
def very_simple_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="📝 Создать заказ",
                                 callback_data="create_order"),
            InlineKeyboardButton(text="📋 Мои заказы", callback_data="my_orders"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


# This is the same keyboard, but created with InlineKeyboardBuilder (preferred way)
def simple_menu_keyboard():
    # First, you should create an InlineKeyboardBuilder object
    keyboard = InlineKeyboardBuilder()

    # You can use keyboard.button() method to add buttons, then enter text and callback_data
    keyboard.button(
        text="📝 Создать заказ",
        callback_data="create_order"
    )
    keyboard.button(
        text="📋 Мои заказы",
        # In this simple example, we use a string as callback_data
        callback_data="my_orders"
    )

    # If needed you can use keyboard.adjust() method to change the number of buttons per row
    # keyboard.adjust(2)

    # Then you should always call keyboard.as_markup() method to get a valid InlineKeyboardMarkup object
    return keyboard.as_markup()


# For a more advanced usage of callback_data, you can use the CallbackData factory
class OrderCallbackData(CallbackData, prefix="order"):
    """
    This class represents a CallbackData object for orders.

    - When used in InlineKeyboardMarkup, you have to create an instance of this class, run .pack() method, and pass to callback_data parameter.

    - When used in InlineKeyboardBuilder, you have to create an instance of this class and pass to callback_data parameter (without .pack() method).

    - In handlers you have to import this class and use it as a filter for callback query handlers, and then unpack callback_data parameter to get the data.

    # Example usage in simple_menu.py
    """
    order_id: int


def my_orders_keyboard(orders: list):
    # Here we use a list of orders as a parameter (from simple_menu.py)

    keyboard = InlineKeyboardBuilder()
    for order in orders:
        keyboard.button(
            text=f"📝 {order['title']}",
            # Here we use an instance of OrderCallbackData class as callback_data parameter
            # order id is the field in OrderCallbackData class, that we defined above
            callback_data=OrderCallbackData(order_id=order["id"])
        )

    return keyboard.as_markup()


def language_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🇷🇺 Русский", callback_data="lang:ru")
    keyboard.button(text="🇺🇿 O'zbek", callback_data="lang:uz")
    return keyboard.as_markup()


def gender_inline_keyboard(lang: str = "ru"):
    from tgbot.i18n import t
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=t(lang, "gender_male"), callback_data="gender:male")
    keyboard.button(text=t(lang, "gender_female"), callback_data="gender:female")
    return keyboard.as_markup()


def activity_inline_keyboard(lang: str = "ru"):
    keyboard = InlineKeyboardBuilder()
    from tgbot.i18n import t
    keyboard.button(text=t(lang, "activity_0"), callback_data="activity:0")
    keyboard.button(text=t(lang, "activity_1"), callback_data="activity:1")
    keyboard.button(text=t(lang, "activity_3"), callback_data="activity:3")
    keyboard.button(text=t(lang, "activity_5"), callback_data="activity:5")
    # Arrange buttons in 2 columns (2x2)
    keyboard.adjust(2)
    return keyboard.as_markup()


def main_menu_inline_keyboard():
    # Legacy: main menu now uses reply keyboard; this function is deprecated
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Анализ тела", callback_data="menu:body")
    keyboard.button(text="🍎 Ежедневная норма", callback_data="menu:norm")
    keyboard.button(text="🔄 Пересчитать", callback_data="menu:recalc")
    keyboard.adjust(1)
    return keyboard.as_markup()


def recalc_inline_keyboard(lang: str = "ru"):
    from tgbot.i18n import t
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=t(lang, "recalc_label"), callback_data="recalc")
    return keyboard.as_markup()


def recalc_confirm_keyboard(lang: str = "ru"):
    from tgbot.i18n import t
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text=t(lang, "recalc_yes"), callback_data="recalc_confirm:yes")
    keyboard.button(text=t(lang, "recalc_no"), callback_data="recalc_confirm:no")
    keyboard.adjust(2)
    return keyboard.as_markup()


# === Клавиатуры для работы с приемами пищи ===

class MealActionCallback(CallbackData, prefix="meal"):
    """Callback data для действий с приемом пищи"""
    action: str  # confirm, edit, cancel
    meal_id: int


class ProductActionCallback(CallbackData, prefix="product"):
    """Callback data для действий с продуктом"""
    action: str  # edit_weight, delete
    item_id: int
    meal_id: int


def meal_confirmation_keyboard(meal_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения приема пищи"""
    keyboard = InlineKeyboardBuilder()

    texts = {
        'ru': {
            'confirm': '✅ Да, добавить',
            'edit': '✏️ Изменить',
            'cancel': '❌ Отменить'
        },
        'uz': {
            'confirm': '✅ Ha, qo\'shish',
            'edit': '✏️ O\'zgartirish',
            'cancel': '❌ Bekor qilish'
        }
    }

    t = texts.get(lang, texts['ru'])

    keyboard.button(
        text=t['confirm'],
        callback_data=MealActionCallback(action='confirm', meal_id=meal_id)
    )
    keyboard.button(
        text=t['edit'],
        callback_data=MealActionCallback(action='edit', meal_id=meal_id)
    )
    keyboard.button(
        text=t['cancel'],
        callback_data=MealActionCallback(action='cancel', meal_id=meal_id)
    )

    keyboard.adjust(1)  # По одной кнопке в ряд
    return keyboard.as_markup()


class PortionCallback(CallbackData, prefix="portion"):
    """Callback data для выбора размера порции"""
    multiplier: str  # "0.5", "0.7", "1.0"
    meal_id: int


def portion_keyboard(meal_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для выбора размера порции"""
    keyboard = InlineKeyboardBuilder()

    texts = {
        'ru': {
            'half': '🍽 Половина порции (0.5)',
            'most': '🍽 Большая часть (0.7)',
            'full': '🍽 Целая порция (1.0)',
            'cancel': '❌ Отменить'
        },
        'uz': {
            'half': '🍽 Yarim porsiya (0.5)',
            'most': '🍽 Katta qism (0.7)',
            'full': '🍽 Butun porsiya (1.0)',
            'cancel': '❌ Bekor qilish'
        }
    }

    t = texts.get(lang, texts['ru'])

    keyboard.button(
        text=t['half'],
        callback_data=PortionCallback(multiplier="0.5", meal_id=meal_id)
    )
    keyboard.button(
        text=t['most'],
        callback_data=PortionCallback(multiplier="0.7", meal_id=meal_id)
    )
    keyboard.button(
        text=t['full'],
        callback_data=PortionCallback(multiplier="1.0", meal_id=meal_id)
    )
    keyboard.button(
        text=t['cancel'],
        callback_data=MealActionCallback(action='cancel', meal_id=meal_id)
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def meal_edit_keyboard(meal_id: int, products: list, lang: str = "ru") -> InlineKeyboardMarkup:
    """Клавиатура для редактирования приема пищи"""
    keyboard = InlineKeyboardBuilder()

    texts = {
        'ru': {
            'back': '◀️ Назад',
            'delete': '🗑 Удалить',
        },
        'uz': {
            'back': '◀️ Orqaga',
            'delete': '🗑 O\'chirish',
        }
    }

    t = texts.get(lang, texts['ru'])

    # Кнопки для каждого продукта
    for item in products:
        keyboard.button(
            text=f"✏️ {item['product_name']} ({item['weight']}г)",
            callback_data=ProductActionCallback(
                action='edit_weight',
                item_id=item['item_id'],
                meal_id=meal_id
            )
        )
        keyboard.button(
            text=t['delete'],
            callback_data=ProductActionCallback(
                action='delete',
                item_id=item['item_id'],
                meal_id=meal_id
            )
        )

    # Кнопка "Назад"
    keyboard.button(
        text=t['back'],
        callback_data=MealActionCallback(action='back_to_confirm', meal_id=meal_id)
    )

    keyboard.adjust(2)  # Продукт и удалить в одном ряду
    return keyboard.as_markup()

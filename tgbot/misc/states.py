from aiogram.fsm.state import State, StatesGroup


class OnboardingStates(StatesGroup):
    """Состояния для процесса онбординга"""
    language = State()
    gender = State()
    birth_date = State()
    height = State()
    weight = State()
    activity_level = State()


class FoodTrackingStates(StatesGroup):
    """Состояния для отслеживания питания"""
    waiting_for_photo = State()
    confirming_meal = State()
    choosing_portion = State()
    editing_product = State()
    editing_weight = State()


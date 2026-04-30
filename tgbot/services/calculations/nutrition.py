from typing import Literal
from .body_analysis import BodyAnalysisCalculator


class NutritionCalculator:
    """Калькулятор для расчета калорий и БЖУ"""
    
    def __init__(self):
        self.body_calc = BodyAnalysisCalculator()
    
    @staticmethod
    def calculate_bmr(
        gender: Literal['male', 'female'],
        weight: float,
        height: int,
        age: int
    ) -> int:
        """
        Рассчитать базовый обмен веществ (BMR) по формуле Mifflin-St Jeor
        
        Мужчины: BMR = 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст (лет) + 5
        Женщины: BMR = 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст (лет) - 161
        """
        base_bmr = 10 * weight + 6.25 * height - 5 * age
        
        if gender == 'male':
            bmr = base_bmr + 5
        else:
            bmr = base_bmr - 161
        
        return int(bmr)
    
    @staticmethod
    def get_activity_multiplier(activity_level: int) -> float:
        """
        Получить коэффициент активности для расчета TDEE
        
        Тренировок в неделю | Коэффициент
        0                   | 1.2
        1-2                 | 1.375
        3-4                 | 1.55
        5+                  | 1.725
        """
        if activity_level == 0:
            return 1.2
        elif activity_level <= 2:
            return 1.375
        elif activity_level <= 4:
            return 1.55
        else:  # 5+
            return 1.725
    
    def calculate_tdee(
        self,
        gender: Literal['male', 'female'],
        weight: float,
        height: int,
        age: int,
        activity_level: int
    ) -> int:
        """
        Рассчитать суточную потребность в калориях (TDEE)
        TDEE = BMR × коэффициент активности
        """
        bmr = self.calculate_bmr(gender, weight, height, age)
        multiplier = self.get_activity_multiplier(activity_level)
        tdee = bmr * multiplier
        return int(tdee)
    
    def calculate_calories_for_weight_loss(self, tdee: int, has_excess_fat: bool = True) -> int:
        """
        Рассчитать калории для похудения или поддержания веса
        Если has_excess_fat=True: используется дефицит -20% от TDEE
        Если has_excess_fat=False: используется TDEE (поддержание веса)
        """
        if has_excess_fat:
            calories = int(tdee * 0.8)
        else:
            calories = tdee
        return calories
    
    def calculate_proteins(self, target_weight: float) -> int:
        """
        Рассчитать белки (г)
        Белки = 2 г на 1 кг целевого веса
        """
        return int(target_weight * 2)
    
    def calculate_fats(self, target_weight: float) -> int:
        """
        Рассчитать жиры (г)
        Жиры = 0.9 г на 1 кг целевого веса
        """
        return int(target_weight * 0.9)
    
    def calculate_carbs(
        self,
        calories: int,
        proteins: int,
        fats: int
    ) -> int:
        """
        Рассчитать углеводы (г)
        Углеводы рассчитываются как остаток калорий после белков и жиров
        1 г белка = 4 ккал
        1 г жира = 9 ккал
        1 г углеводов = 4 ккал
        """
        protein_calories = proteins * 4
        fat_calories = fats * 9
        carb_calories = calories - protein_calories - fat_calories
        carbs = int(carb_calories / 4)
        return max(0, carbs)
    
    def calculate_weight_loss_time(
        self,
        fat_to_lose: float,
        tdee: int,
        calories_for_weight_loss: int
    ) -> dict:
        """
        Рассчитать ориентировочное время для похудения
        
        Returns:
            dict с ключами:
                - fat_loss_per_week: скорость потери жира (кг/нед)
                - weeks_needed: количество недель
                - display_text: форматированный текст для отображения
        """
        if fat_to_lose <= 0:
            return {
                'fat_loss_per_week': 0,
                'weeks_needed': 0,
                'display_text': ''
            }
        
        # Дневной дефицит
        daily_deficit = tdee - calories_for_weight_loss
        
        # Недельный дефицит
        weekly_deficit = daily_deficit * 7
        
        # Скорость потери жира (кг/неделю)
        fat_loss_per_week = weekly_deficit / 7700
        
        # Ограничение безопасности: не более 1 кг/неделю
        if fat_loss_per_week > 1.0:
            fat_loss_per_week = 1.0
        
        # Количество недель для достижения цели
        weeks_needed = fat_to_lose / fat_loss_per_week
        
        # Форматирование диапазона скорости потери жира
        fat_loss_min = max(0.1, fat_loss_per_week * 0.9)  # -10% для диапазона
        fat_loss_max = min(1.0, fat_loss_per_week * 1.1)  # +10% для диапазона, но не более 1.0
        
        # Форматирование результата
        if weeks_needed < 8:
            # Показываем в неделях
            weeks_min = max(1, int(weeks_needed * 0.85))  # -15% для диапазона
            weeks_max = int(weeks_needed * 1.15)  # +15% для диапазона
            display_text = (
                f"При текущем дефиците лишний жир будет уходить "
                f"примерно со скоростью {fat_loss_min:.1f}–{fat_loss_max:.1f} кг в неделю.\n"
                f"Ориентировочное время достижения цели — {weeks_min}–{weeks_max} недель.\n"
                f"Это ориентир, а не гарантия результата."
            )
        else:
            # Показываем в месяцах
            months_min = max(1, int((weeks_needed * 0.85) / 4.33))  # -15% для диапазона
            months_max = max(months_min + 1, int((weeks_needed * 1.15) / 4.33))  # +15% для диапазона
            
            display_text = (
                f"При текущем дефиците лишний жир будет уходить "
                f"примерно со скоростью {fat_loss_min:.1f}–{fat_loss_max:.1f} кг в неделю.\n"
                f"Ориентировочное время достижения цели — {months_min}–{months_max} месяцев.\n"
                f"Это ориентир, а не гарантия результата."
            )
        
        return {
            'fat_loss_per_week': round(fat_loss_per_week, 2),
            'weeks_needed': round(weeks_needed, 1),
            'display_text': display_text
        }
    
    def calculate_all(
        self,
        gender: Literal['male', 'female'],
        birth_date,
        height: int,
        weight: float,
        activity_level: int,
        target_weight: float,
        excess_fat_kg: float
    ) -> dict:
        """
        Рассчитать все параметры питания
        
        Returns:
            dict с ключами:
                - bmr: базовый обмен веществ
                - tdee: суточная потребность
                - calories: калории для похудения
                - proteins: белки (г)
                - fats: жиры (г)
                - carbs: углеводы (г)
                - recommended_months: рекомендуемое количество месяцев для похудения
        """
        age = self.body_calc.calculate_age(birth_date)
        
        bmr = self.calculate_bmr(gender, weight, height, age)
        tdee = self.calculate_tdee(gender, weight, height, age, activity_level)

        # Определяем, есть ли лишний вес
        has_excess_fat = excess_fat_kg > 0
        calories = self.calculate_calories_for_weight_loss(tdee, has_excess_fat)

        proteins = self.calculate_proteins(target_weight)
        fats = self.calculate_fats(target_weight)
        carbs = self.calculate_carbs(calories, proteins, fats)
        
        weight_loss_time = self.calculate_weight_loss_time(
            fat_to_lose=excess_fat_kg,
            tdee=tdee,
            calories_for_weight_loss=calories
        )
        
        return {
            'bmr': bmr,
            'tdee': tdee,
            'calories': calories,
            'proteins': proteins,
            'fats': fats,
            'carbs': carbs,
            'weight_loss_time': weight_loss_time
        }


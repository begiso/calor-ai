from datetime import date
from typing import Literal


class BodyAnalysisCalculator:
    """Калькулятор для анализа состава тела"""
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """Рассчитать возраст по дате рождения"""
        today = date.today()
        age = today.year - birth_date.year
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        return age
    
    @staticmethod
    def calculate_bmi(weight: float, height: int) -> float:
        """
        Рассчитать индекс массы тела (ИМТ)
        ИМТ = вес (кг) / рост (м)²
        """
        height_m = height / 100
        return round(weight / (height_m ** 2), 1)
    
    @staticmethod
    def calculate_body_fat_percentage(
        bmi: float,
        age: int,
        gender: Literal['male', 'female']
    ) -> float:
        """
        Рассчитать процент жира по формуле Deurenberg
        Формула: (1.20 × ИМТ) + (0.23 × возраст) - (10.8 × пол) - 5.4
        где пол: мужчина = 1, женщина = 0
        """
        gender_coefficient = 1 if gender == 'male' else 0
        body_fat = (1.20 * bmi) + (0.23 * age) - (10.8 * gender_coefficient) - 5.4
        # Ограничиваем разумными значениями
        body_fat = max(5.0, min(50.0, body_fat))
        return round(body_fat, 1)
    
    @staticmethod
    def calculate_lean_body_mass(
        weight: float,
        body_fat_percentage: float
    ) -> float:
        """
        Рассчитать безжировую массу тела
        БММ = вес × (1 - процент жира / 100)
        """
        lean_mass = weight * (1 - body_fat_percentage / 100)
        return round(lean_mass, 1)
    
    @staticmethod
    def get_target_body_fat_percentage(gender: Literal['male', 'female']) -> float:
        """
        Получить целевой процент жира
        Мужчина: 15%
        Женщина: 23%
        """
        return 15.0 if gender == 'male' else 23.0
    
    @staticmethod
    def calculate_target_weight(
        lean_body_mass: float,
        target_body_fat_percentage: float
    ) -> float:
        """
        Рассчитать целевой вес при сохранении безжировой массы
        Целевой вес = БММ / (1 - целевой процент жира / 100)
        """
        target_weight = lean_body_mass / (1 - target_body_fat_percentage / 100)
        return round(target_weight, 1)
    
    @staticmethod
    def calculate_excess_fat(
        current_weight: float,
        target_weight: float
    ) -> float:
        """
        Рассчитать реальный лишний вес (жир)
        Лишний жир = текущий вес - целевой вес
        """
        excess = current_weight - target_weight
        return round(max(0, excess), 1)
    
    def calculate_all(
        self,
        gender: Literal['male', 'female'],
        birth_date: date,
        height: int,
        weight: float
    ) -> dict:
        """
        Рассчитать все параметры анализа тела
        
        Returns:
            dict с ключами:
                - age: возраст
                - bmi: ИМТ
                - body_fat_percentage: процент жира
                - lean_body_mass: безжировая масса
                - target_body_fat_percentage: целевой процент жира
                - target_weight: целевой вес
                - excess_fat: лишний жир (кг)
        """
        age = self.calculate_age(birth_date)
        bmi = self.calculate_bmi(weight, height)
        body_fat_percentage = self.calculate_body_fat_percentage(bmi, age, gender)
        lean_body_mass = self.calculate_lean_body_mass(weight, body_fat_percentage)
        target_body_fat_percentage = self.get_target_body_fat_percentage(gender)
        target_weight = self.calculate_target_weight(lean_body_mass, target_body_fat_percentage)
        excess_fat = self.calculate_excess_fat(weight, target_weight)
        
        return {
            'age': age,
            'bmi': bmi,
            'body_fat_percentage': body_fat_percentage,
            'lean_body_mass': lean_body_mass,
            'target_body_fat_percentage': target_body_fat_percentage,
            'target_weight': target_weight,
            'excess_fat': excess_fat
        }


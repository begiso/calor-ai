import os
import json
import logging
from typing import List, Dict, Optional
from io import BytesIO

import google.generativeai as genai
from PIL import Image

logger = logging.getLogger(__name__)


class FoodAnalyzer:
    """Сервис для анализа фото еды с помощью Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация анализатора еды

        Args:
            api_key: API ключ для Gemini. Если не указан, берется из переменной окружения GEMINI_API_KEY
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=self.api_key)
        # Используем gemini-2.5-flash для анализа изображений (поддерживает multimodal)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_food_photo(self, image_bytes: bytes) -> Dict:
        """
        Анализирует фото еды и возвращает информацию о продуктах

        Args:
            image_bytes: Байты изображения

        Returns:
            Dict с информацией о распознанных продуктах
        """
        try:
            # Открываем изображение
            image = Image.open(BytesIO(image_bytes))

            # Создаем промт для анализа
            prompt = self._create_analysis_prompt()

            # Отправляем запрос к Gemini
            response = self.model.generate_content([prompt, image])

            # Парсим ответ
            result = self._parse_response(response.text)

            return result

        except Exception as e:
            logger.error(f"Error analyzing food photo: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': []
            }

    def _create_analysis_prompt(self) -> str:
        """Создает промт для анализа фото еды"""
        return """Проанализируй это изображение и определи, есть ли на нём ЕДА или НАПИТКИ.

КРИТИЧЕСКИ ВАЖНО:
- Если на фото НЕТ еды или напитков (например: люди, животные, предметы, природа, селфи, мебель, одежда и т.д.), верни:
  {"success": false, "error": "На фото не обнаружена еда", "products": []}

- Если на фото ЕСТЬ еда или напитки, проанализируй:

1. Какие продукты/блюда видны на фото
2. Примерный вес каждого продукта в граммах
3. Калорийность и БЖУ для каждого продукта
4. Уровень уверенности в распознавании (от 0 до 1)

ПРАВИЛА РАСПОЗНАВАНИЯ:
- Распознавай ТОЛЬКО видимые продукты и блюда
- НЕ угадывай скрытые ингредиенты в сложных блюдах
- Если продукт виден частично, укажи низкую уверенность (0.3-0.5)
- Используй стандартные порции для оценки веса
- Калорийность и БЖУ рассчитывай на указанный вес
- Если видна только упаковка без самого продукта - это НЕ еда

Верни результат СТРОГО в формате JSON:
{
  "success": true,
  "products": [
    {
      "name": "Название продукта на русском",
      "weight": 280,
      "calories": 480,
      "proteins": 17.0,
      "fats": 20.0,
      "carbs": 58.0,
      "confidence": 0.85
    }
  ]
}

ВАЖНО: Ответ должен быть ТОЛЬКО валидным JSON, без дополнительного текста!"""

    def _parse_response(self, response_text: str) -> Dict:
        """
        Парсит ответ от Gemini

        Args:
            response_text: Текст ответа от API

        Returns:
            Dict с распознанными продуктами
        """
        try:
            # Убираем markdown форматирование если есть
            text = response_text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()

            # Парсим JSON
            result = json.loads(text)

            # Валидация результата
            if not isinstance(result, dict):
                raise ValueError("Response is not a dictionary")

            if 'success' not in result:
                result['success'] = True

            if 'products' not in result:
                result['products'] = []

            # Валидация каждого продукта
            validated_products = []
            for product in result.get('products', []):
                if self._validate_product(product):
                    validated_products.append(product)
                else:
                    logger.warning(f"Invalid product data: {product}")

            result['products'] = validated_products

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            return {
                'success': False,
                'error': f'Ошибка парсинга ответа: {str(e)}',
                'products': []
            }
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': []
            }

    def _validate_product(self, product: Dict) -> bool:
        """
        Валидирует данные продукта

        Args:
            product: Данные продукта

        Returns:
            True если данные валидны
        """
        required_fields = ['name', 'weight', 'calories', 'proteins', 'fats', 'carbs']

        # Проверяем наличие обязательных полей
        for field in required_fields:
            if field not in product:
                return False

        # Проверяем типы данных
        try:
            weight = int(product['weight'])
            calories = int(product['calories'])
            proteins = float(product['proteins'])
            fats = float(product['fats'])
            carbs = float(product['carbs'])

            # Проверяем разумность значений
            if weight <= 0 or weight > 5000:  # вес от 1г до 5кг
                return False
            if calories < 0 or calories > 10000:
                return False
            if proteins < 0 or proteins > 1000:
                return False
            if fats < 0 or fats > 1000:
                return False
            if carbs < 0 or carbs > 1000:
                return False

            # Проверяем confidence (по умолчанию 1.0)
            confidence = float(product.get('confidence', 1.0))
            if confidence < 0 or confidence > 1:
                product['confidence'] = 1.0

            return True

        except (ValueError, TypeError):
            return False

    def recalculate_nutrition(self, product: Dict, new_weight: int) -> Dict:
        """
        Пересчитывает БЖУ и калории для нового веса

        Args:
            product: Данные продукта
            new_weight: Новый вес в граммах

        Returns:
            Обновленные данные продукта
        """
        old_weight = product['weight']
        ratio = new_weight / old_weight

        return {
            'name': product['name'],
            'weight': new_weight,
            'calories': round(product['calories'] * ratio),
            'proteins': round(product['proteins'] * ratio, 1),
            'fats': round(product['fats'] * ratio, 1),
            'carbs': round(product['carbs'] * ratio, 1),
            'confidence': product.get('confidence', 1.0)
        }

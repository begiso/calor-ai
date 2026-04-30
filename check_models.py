import os
import google.generativeai as genai

# Загружаем API ключ
api_key = os.getenv('GEMINI_API_KEY') or 'AIzaSyDDsMmVkxhcIFZXfK_XIKOQ-dLcxoP0oeI'

genai.configure(api_key=api_key)

print("Доступные модели Gemini:")
print("=" * 50)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"\n✅ {model.name}")
        print(f"   Описание: {model.description}")
        print(f"   Методы: {model.supported_generation_methods}")

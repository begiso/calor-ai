# calorAI - Telegram бот для управления весом и планирования питания

Telegram бот для расчета состава тела, целевого веса и персонализированных рекомендаций по питанию, разработанный с использованием библиотеки [`aiogram v3.0+`](https://github.com/aiogram/aiogram/tree/dev-3.x).

## 🎯 Возможности бота

- 📊 **Анализ состава тела**: расчет ИМТ, процента жира, сухой массы тела
- 🎯 **Определение целевого веса**: на основе оптимального процента жира
- 🍎 **Персонализированный план питания**: калории и макронутриенты (белки, жиры, углеводы)
- 📸 **Подсчет калорий по фото**: анализ еды с помощью AI (Gemini), автоматический расчет КБЖУ
- ✅ **Отслеживание питания**: подтверждение, редактирование и отмена приемов пищи
- 📈 **Дневная статистика**: контроль потребленных калорий и оставшейся нормы
- ⏱️ **Прогноз времени**: оценка времени достижения целевого веса
- 🌍 **Мультиязычность**: поддержка русского и узбекского языков

## 📐 Используемые формулы

- **Процент жира в теле**: формула Deurenberg (с учетом пола и возраста)
- **Базовый метаболизм (BMR)**: уравнение Mifflin-St Jeor
- **Общий расход энергии (TDEE)**: BMR × коэффициент активности
- **План похудения**: дефицит калорий 20%, распределение макронутриентов

## 🚀 Быстрый старт

### Для начала работы:

1. **Создайте файл `.env`** на основе `.env.example` и заполните необходимые данные:
   ```env
   BOT_TOKEN=your_bot_token_here
   ADMINS=123456789,987654321
   DB_PATH=data/database.db
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

   **Важно:** Для работы функции подсчета калорий по фото необходим API ключ от Google Gemini.
   Получить его можно на [Google AI Studio](https://makersuite.google.com/app/apikey).

2. **Выберите способ запуска:**

   #### С Docker (рекомендуется):
   Если у вас нет Docker, [скачайте и установите его](https://docs.docker.com/get-docker/).
   ```bash
   docker-compose up
   ```

   #### Без Docker:
   ```bash
   # Создайте виртуальное окружение
   python3 -m venv venv
   source venv/bin/activate  # для Windows: venv\Scripts\activate

   # Установите зависимости
   pip install -r requirements.txt

   # Запустите бота
   python3 bot.py
   ```

## 📁 Структура проекта

```
calorai/
├── bot.py                          # Точка входа приложения
├── tgbot/
│   ├── config.py                   # Конфигурация бота
│   ├── handlers/                   # Обработчики команд и сообщений
│   │   ├── admin.py               # Команды для администраторов
│   │   ├── onboarding.py          # Процесс сбора данных пользователя
│   │   ├── food_tracking.py       # Подсчет калорий по фото
│   │   ├── results.py             # Отображение результатов расчетов
│   │   └── user.py                # Пользовательские команды
│   ├── services/                   # Бизнес-логика
│   │   ├── food_analyzer.py       # AI анализ фото еды (Gemini)
│   │   └── calculations/          # Расчетные модули
│   │       ├── body_analysis.py   # Анализ состава тела
│   │       └── nutrition.py       # Расчет питания
│   ├── models/                     # Модели данных
│   │   ├── user.py                # Модель пользователя (SQLite)
│   │   └── meal.py                # Модель приемов пищи
│   ├── keyboards/                  # Клавиатуры Telegram
│   │   ├── reply.py               # Reply-клавиатуры
│   │   └── inline.py              # Inline-клавиатуры
│   ├── middlewares/                # Middleware
│   ├── filters/                    # Кастомные фильтры
│   └── misc/                       # Вспомогательные модули
│       └── states.py              # FSM состояния для диалогов
└── infrastructure/                 # Дополнительная инфраструктура
```

## 🛠️ Разработка

### Как создавать и регистрировать обработчики:

1. **Создайте модуль** `your_handler.py` в папке `tgbot/handlers/`

2. **Создайте роутер** в вашем модуле:
   ```python
   from aiogram import Router

   my_router = Router()
   ```

3. **Зарегистрируйте обработчики** с помощью декораторов:
   ```python
   from aiogram import types
   from aiogram.filters import Command

   @my_router.message(Command("start"))
   async def cmd_start(message: types.Message):
       await message.reply("Привет! Я помогу тебе рассчитать план питания!")
   ```

4. **Добавьте роутер** в файл `tgbot/handlers/__init__.py`:
   ```python
   from .admin import admin_router
   from .onboarding import onboarding_router
   from .results import results_router
   from .user import user_router
   from .your_handler import my_router  # ваш новый роутер
   from .echo import echo_router

   routers_list = [
       admin_router,
       onboarding_router,
       results_router,
       user_router,
       my_router,           # добавьте сюда
       echo_router,         # echo_router должен быть последним!
   ]
   ```

   **Важно:** Порядок роутеров имеет значение! Роутер `echo_router` должен быть последним, так как он обрабатывает все необработанные сообщения.

### Работа с базой данных

Проект использует простую SQLite базу данных с прямыми SQL-запросами для максимальной производительности и простоты.

**Модель пользователя** (`tgbot/models/user.py`) включает:
- Демографические данные (возраст, пол, рост, вес)
- Уровень физической активности
- Дневная норма калорий и макронутриентов
- Предпочитаемый язык
- Временные метки создания/обновления

**Модель приемов пищи** (`tgbot/models/meal.py`) включает:
- Таблица `meals`: приемы пищи со статусом (draft/confirmed)
- Таблица `meal_items`: продукты в каждом приеме пищи
- Автоматический расчет суммарных КБЖУ
- Методы для редактирования и подтверждения приемов

**Операции с БД:**
```python
from tgbot.models.user import UserModel
from tgbot.models.meal import MealModel

# Работа с пользователем
user_model = UserModel()
user = user_model.get_user(user_id)
user_model.create_or_update_user(user_id, **kwargs)

# Работа с приемами пищи
meal_model = MealModel()
meal_id = meal_model.create_meal(user_id, photo_file_id)
meal_model.add_meal_item(meal_id, product_name, weight, calories, proteins, fats, carbs)
meal_model.confirm_meal(meal_id)
stats = meal_model.get_daily_stats(user_id)
```

### Как работает подсчет калорий по фото

1. **Пользователь отправляет фото еды** в бот
2. **FoodAnalyzer** отправляет фото в Gemini API с промптом для анализа
3. **AI распознает** продукты, оценивает вес и рассчитывает КБЖУ
4. **Создается черновик** приема пищи со статусом `draft`
5. **Пользователь видит** результат и может:
   - ✅ Подтвердить и добавить в дневной баланс
   - ✏️ Отредактировать вес продуктов или удалить продукты
   - ❌ Отменить прием пищи
6. **После подтверждения** калории добавляются к дневной статистике

**Важно:** Gemini API может давать приблизительные результаты (±10-20%), поэтому пользователь всегда может скорректировать данные.

### Расширенная инфраструктура (опционально)

В папке `infrastructure/` находятся готовые модули для масштабирования:
- **PostgreSQL + SQLAlchemy**: для более сложных запросов и связей
- **Alembic**: система миграций базы данных
- **FastAPI**: для создания API endpoints
- **Redis**: для кеширования и хранения состояний
- **Nginx**: для работы в webhook режиме

## 📚 Полезные ресурсы

### Документация aiogram v3
- [Официальная документация aiogram](https://docs.aiogram.dev/)
- [Руководство от Groosha](https://mastergroosha.github.io/aiogram-3-guide) (на русском)

### Научные ресурсы
- [Формула Mifflin-St Jeor](https://en.wikipedia.org/wiki/Basal_metabolic_rate)
- [Формула Deurenberg для процента жира](https://pubmed.ncbi.nlm.nih.gov/1992112/)

## 🚀 Деплой в продакшн

Подробная инструкция по деплою бота на различные платформы находится в файле [DEPLOYMENT.md](DEPLOYMENT.md).

### Быстрый деплой на Railway.app:

1. Залейте код на GitHub
2. Зарегистрируйтесь на [Railway.app](https://railway.app)
3. Создайте новый проект из GitHub репозитория
4. Добавьте переменные окружения:
   - `BOT_TOKEN`
   - `ADMIN_IDS`
   - `GEMINI_API_KEY`
5. Готово! Бот автоматически запустится

📖 **Подробные инструкции для других платформ** (Render, VPS, Docker) смотрите в [DEPLOYMENT.md](DEPLOYMENT.md)

## 🤝 Вклад в проект

Если вы нашли ошибку или хотите предложить улучшение:
1. Создайте Issue с описанием проблемы
2. Форкните репозиторий
3. Создайте ветку для вашей функции
4. Отправьте Pull Request

## 📝 Лицензия

Этот проект создан на основе aiogram 3.0 template.

---

**Приятной разработки! 🚀**

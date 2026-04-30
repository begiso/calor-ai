# 🚀 Деплой CalorAI бота

## Вариант 1: Railway.app (Рекомендуется)

### Преимущества:
- ✅ Бесплатно (500 часов/месяц)
- ✅ Автоматический деплой из GitHub
- ✅ Простая настройка
- ✅ Постоянно работает (не засыпает)

### Шаги:

1. **Залейте код на GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/ваш-username/CalorAI.git
   git push -u origin main
   ```

2. **Зарегистрируйтесь на Railway**
   - Перейдите на https://railway.app
   - Войдите через GitHub

3. **Создайте новый проект**
   - Нажмите "New Project"
   - Выберите "Deploy from GitHub repo"
   - Выберите репозиторий CalorAI

4. **Добавьте переменные окружения**
   - Перейдите в Settings → Variables
   - Добавьте:
     ```
     BOT_TOKEN=ваш_токен_от_BotFather
     ADMIN_IDS=ваш_telegram_id
     GEMINI_API_KEY=ваш_gemini_api_key
     ```

5. **Деплой!**
   - Railway автоматически соберет и запустит бота
   - Проверьте логи в разделе "Deployments"

---

## Вариант 2: Render.com

### Преимущества:
- ✅ Бесплатно
- ✅ Автоматический деплой из GitHub
- ⚠️ Засыпает после 15 минут неактивности

### Шаги:

1. **Залейте код на GitHub** (как в варианте 1)

2. **Зарегистрируйтесь на Render**
   - Перейдите на https://render.com
   - Войдите через GitHub

3. **Создайте новый Web Service**
   - New → Background Worker
   - Подключите GitHub репозиторий
   - Название: CalorAI
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python3 bot.py`

4. **Добавьте переменные окружения**
   - В разделе Environment добавьте:
     ```
     BOT_TOKEN
     ADMIN_IDS
     GEMINI_API_KEY
     ```

5. **Деплой!**

---

## Вариант 3: VPS (DigitalOcean, Hetzner, Timeweb)

### Преимущества:
- ✅ Полный контроль
- ✅ Не засыпает
- ✅ Высокая производительность

### Стоимость:
- ~$5-10/месяц

### Шаги:

1. **Создайте сервер** (Ubuntu 22.04)

2. **Подключитесь по SSH**
   ```bash
   ssh root@ваш_ip
   ```

3. **Установите зависимости**
   ```bash
   apt update
   apt install -y python3 python3-pip git
   ```

4. **Клонируйте репозиторий**
   ```bash
   cd /opt
   git clone https://github.com/ваш-username/CalorAI.git
   cd CalorAI
   ```

5. **Создайте .env файл**
   ```bash
   nano .env
   ```
   Добавьте:
   ```
   BOT_TOKEN=ваш_токен
   ADMIN_IDS=ваш_id
   GEMINI_API_KEY=ваш_ключ
   ```

6. **Установите зависимости**
   ```bash
   pip3 install -r requirements.txt
   ```

7. **Создайте systemd сервис**
   ```bash
   nano /etc/systemd/system/calorAI.service
   ```

   Вставьте:
   ```ini
   [Unit]
   Description=CalorAI Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=root
   WorkingDirectory=/opt/CalorAI
   ExecStart=/usr/bin/python3 /opt/CalorAI/bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

8. **Запустите сервис**
   ```bash
   systemctl daemon-reload
   systemctl enable calorAI
   systemctl start calorAI
   systemctl status calorAI
   ```

9. **Проверьте логи**
   ```bash
   journalctl -u calorAI -f
   ```

---

## Обновление бота

### Railway/Render:
- Просто сделайте `git push` - автоматически задеплоится

### VPS:
```bash
cd /opt/CalorAI
git pull
systemctl restart calorAI
```

---

## Проверка работы

После деплоя:
1. Откройте бота в Telegram
2. Отправьте `/start`
3. Пройдите онбординг
4. Проверьте отправку фото еды

---

## Мониторинг

### Railway:
- Логи: Dashboard → Deployments → Logs

### Render:
- Логи: Dashboard → Logs

### VPS:
```bash
journalctl -u calorAI -f
```

---

## Решение проблем

### Бот не отвечает:
1. Проверьте логи
2. Убедитесь, что переменные окружения заданы
3. Проверьте, что токен бота правильный

### Ошибка "Conflict: terminated by other getUpdates":
- Остановите все другие экземпляры бота
- Только один экземпляр может работать одновременно

### База данных пропадает при рестарте:
- На Railway/Render создайте Volume для папки `data/`
- Или используйте PostgreSQL вместо SQLite

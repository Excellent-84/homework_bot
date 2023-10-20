### Telegram-бот

Бот раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.
При обновлении статуса анализирует ответ API и отправляет пользователю соответствующее уведомление в Telegram.
Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

### Стек технологий:
* ##### Python
* ##### python-telegram-bot

### Как запустить проект:
#### Клонировать репозиторий и перейти в него в командной строке:
``` 
git clone https://github.com/Excellent-84/homework_bot.git
``` 

#### Cоздать и активировать виртуальное окружение:
``` 
cd homework_bot
python -m venv venv
source venv/bin/activate
``` 

#### Установить зависимости из файла requirements.txt:
``` 
python -m pip install --upgrade pip
pip install -r requirements.txt
``` 

#### Создать файл .env и указать необходимые токены по примеру .env.example:
``` 
touch .env
```

#### Запустить проект:
``` 
python homework.py
``` 

#### Автор: [Горин Евгений](https://github.com/Excellent-84)

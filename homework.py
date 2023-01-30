import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('TOKEN_PR')
TELEGRAM_TOKEN = os.getenv('TOKEN_TM')
TELEGRAM_CHAT_ID = os.getenv('CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(message)s',
    filemode='w',
    filename='main.log'
)

handler = logging.StreamHandler(stream=sys.stdout)


def check_tokens():
    """Проверяем доступность переменных."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    logging.info('Отправляем сообщение')
    chat_id = TELEGRAM_CHAT_ID
    text = message
    try:
        bot.send_message(chat_id, text)
        logging.debug(f'Сообщение отправлено: {message}')
    except Exception as error:
        logging.error(f'Ошибка отправки сообщения: {error}')


def get_api_answer(timestamp):
    """Делаем запрос к единственному эндпоинту API-сервиса."""
    logging.info('Делаем запрос к API')
    parametrs = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT, headers=HEADERS, params=parametrs
        )
    except Exception as error:
        raise Exception(f'Ошибка при запросе к эндпоинту API: {error}')
    if response.status_code != HTTPStatus.OK:
        raise ConnectionError('Эндпоинт не доступен')
    return response.json()


def check_response(response):
    """Проверяем ответ API на соответствие документации."""
    logging.info('Проверяем запрос к API')
    if not isinstance(response, dict):
        raise TypeError('Структура данных не соответствует ожиданиям')
    if 'homeworks' not in response:
        raise KeyError('Ошибка ключа "homeworks"')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Под ключом `homeworks` данные не в виде списка')
    try:
        homework = response['homeworks']
    except IndexError:
        raise IndexError('Список пуст')
    return homework


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней работе статус работы."""
    logging.info('Извлекаем данные из запроса')
    try:
        homework_name = homework['homework_name']
    except KeyError:
        raise KeyError('В ответе API нет ключа "homework_name"')
    try:
        homework_status = homework['status']
    except KeyError:
        raise KeyError('В ответе API нет ключа "status"')
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        KeyError('В ответе API отсутствует статус')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Ошибкв проверки ключа')
        raise sys.exit('Проверьте токены')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            message = parse_status(homework[0])
            if message != last_message:
                logging.debug('Отсутствие в ответе новых статусов')
                send_message(bot, message)
                last_message = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

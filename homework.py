import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions

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


def check_tokens():
    """Проверяем доступность переменных."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    logging.info('Отправляем сообщение')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        logging.error('Ошибка отправки сообщения', exc_info=True)
    else:
        logging.debug(f'Сообщение отправлено: {message}')


def get_api_answer(timestamp):
    """Делаем запрос к единственному эндпоинту API-сервиса."""
    logging.info('Делаем запрос к API')
    parametrs = {'from_date': timestamp}
    try:
        response = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=parametrs
        )
    except Exception as error:
        raise exceptions.EndpointNotAvailable(
            f'Ошибка при запросе к {ENDPOINT},'
            f'{HEADERS}, {timestamp} API: {error}'
        )
    if response.status_code != HTTPStatus.OK:
        error = (
            f'{ENDPOINT}, {HEADERS}, {timestamp} не доступен'
            f'{response.status_code}'
        )
        raise exceptions.HTTPStatusError(error)
    return response.json()


def check_response(response):
    """Проверяем ответ API на соответствие документации."""
    logging.info('Проверяем запрос к API')
    if not isinstance(response, dict):
        raise TypeError('Структура данных не соответствует ожиданиям')
    if 'homeworks' not in response:
        raise KeyError('Ошибка ключа "homeworks"')
    if 'current_date' not in response:
        raise KeyError('Ошибка ключа "current_date"')
    if not isinstance(response['homeworks'], list):
        raise TypeError('Под ключом `homeworks` данные не в виде списка')
    return response['homeworks']


def parse_status(homework):
    """Извлекаем из информации о конкретной домашней работе статус работы."""
    logging.info('Извлекаем данные из запроса')
    if 'homework_name' not in homework:
        raise KeyError('В ответе API нет ключа "homework_name"')
    homework_name = homework['homework_name']
    if 'status' not in homework:
        raise KeyError('В ответе API нет ключа "status"')
    homework_status = homework['status']
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError('В ответе API отсутствует статус')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        message = 'Ошибка проверки токенов'
        logging.critical(message)
        raise sys.exit(message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if homework != []:
                message = parse_status(homework[0])
            else:
                message = 'Список работ пуст'
            if message != last_message:
                send_message(bot, message)
                timestamp = int(time.time())
                last_message = message
            else:
                logging.debug('Отсутствие в ответе новых статусов')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message, exc_info=True)
            if message != last_message:
                send_message(bot, message)
                last_message = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()

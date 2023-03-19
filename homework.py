import logging
import os
import sys
import time
import telegram
import requests

from dotenv import load_dotenv
from exception import (
    ApiAnswerError,
    NoElementList,
    RequestError,
    SendMessageError)
from http import HTTPStatus
from requests import RequestException
from telegram import TelegramError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 3
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """
    Функция проверяет, доступны ли данные переменные.
    Если не доступны, выпадет исключение.
    """
    return all([
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID]
    )


def send_message(bot, message) -> None:
    """Функция для отправки сообщений из бота."""
    try:
        logging.debug('Готовимся отправить сообщение.')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logging.debug('Сообщение успешно отправлено.')
    except TelegramError as error:
        logging.error(f'Упс, я не смог отправить сообщение. {error}')
        raise SendMessageError(f'Упс, я не смог отправить сообщение. {error}')


def get_api_answer(timestamp) -> dict:
    """
    Делаем запрос к серверу с домашкой.
    Если он не работает, то выдаст ошибку.
    """
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            logging.error('API Не отвечает.')
            raise ApiAnswerError('API Не отвечает.')
        return response.json()
    except RequestException as error:
        logging.error(f'Ошибка запроса к API {error}')
        raise RequestError(
            f'Ошибка запроса к API {error}'
        )


def check_response(response) -> dict:
    """
    Проверим, что ответ API соответствует документации.
    Обработаем возможные исключения.
    """
    if not isinstance(response, dict):
        logging.error('Неверный тип ответа API.')
        raise TypeError('Неверный тип ответа API.')
    if not isinstance(response.get('homeworks'), list):
        logging.error('Неверный тип ответа homworks.')
        raise TypeError('Неверный тип ответа homworks.')
    return response


def parse_status(homework) -> str:
    """
    Проверим статус домашней работы.
    Обработаем возможные исключения.
    """
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        logging.error('Значение отсутсвует в списке homwork.')
        raise NoElementList('Значение отсутсвует в списке homwork.')
    if homework_status not in HOMEWORK_VERDICTS:
        logging.error('Данный статус отсутствует в словаре.')
        raise KeyError('Нет такого ключа в словаре.')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        logging.critical('Не все нужные переменные присутствуют.')
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    last_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                if last_message != message:
                    send_message(bot, message)
                    last_message = message
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if last_error != message:
                send_message(bot, message)
                last_error = message
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s, %(name)s, %(levelname)s, %(message)s',
        handlers=[
            logging.FileHandler("program.log", encoding='utf-8', mode='w'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    main()

import os
import requests
from time import sleep
import telegram
from dotenv import load_dotenv
import logging


def send_notification(response, bot, chat_id):
    new_attempt = response["new_attempts"][0]
    lesson_title = new_attempt["lesson_title"]
    is_negative = new_attempt["is_negative"]
    lesson_url = new_attempt["lesson_url"]
    if is_negative:
        bot.send_message(chat_id=chat_id, text=f"У вас проверили работу '{lesson_title}'. К сожалению, в работе нашлись ошибки. Ссылка на задачу: {lesson_url}")
    if not is_negative:
        bot.send_message(chat_id=chat_id, text=f"У вас проверили работу '{lesson_title}'. Преподавателю всё понравилось, можно приступать к следующему уроку!")

            
def fetch_response(url, headers, params=None):
    response = requests.get(url=url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def main():
    class TelegramLogsHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            bot.send_message(chat_id, log_entry)

    load_dotenv()
    telegram_token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['CHAT_ID']
    devman_token = os.environ['DEVMAN_TOKEN']
    bot = telegram.Bot(token=telegram_token)
    headers = {"Authorization": f"Token {devman_token}"}
    url = "https://dvmn.org/api/long_polling/"
    logger = logging.getLogger("Логер")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler())
    logger.info("Бот запущен")

    while True:
        try:
            response = fetch_response(url, headers)
            if response["status"] == "found":
                params = {"timestamp": response["new_attempts"][0]["timestamp"]}
                send_notification(response, bot, chat_id)
            else:
                params = {"timestamp": response["timestamp_to_request"]}
            response = fetch_response(url, headers, params)
        except requests.exceptions.ReadTimeout:
            continue
        except requests.exceptions.ConnectionError:
            sleep(10)
            continue
        except Exception as error:
            logger.exception(f"Бот упал с ошибкой:\n{error}")


if __name__ == '__main__':
    main()

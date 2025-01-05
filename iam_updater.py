import requests
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv, set_key, find_dotenv
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='iam_updater.log',
    encoding='utf-8'
)

def get_iam_token(oauth_token):
    """Получение IAM токена через OAuth"""
    url = 'https://iam.api.cloud.yandex.net/iam/v1/tokens'
    data = {"yandexPassportOauthToken": oauth_token}

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json().get('iamToken')
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при получении IAM токена: {e}")
        return None


def update_env_file(iam_token):
    """Обновление IAM токена в .env файле"""
    try:
        dotenv_path = find_dotenv()
        set_key(dotenv_path, 'IAM', iam_token)
        set_key(dotenv_path, 'IAM_UPDATE_TIME', datetime.now().isoformat())
        logging.info("IAM токен успешно обновлен в .env файле")
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении .env файла: {e}")
        return False


def check_iam_token():
    """Проверка актуальности IAM токена"""
    try:
        load_dotenv()
        iam_token = os.getenv('IAM')
        update_time = os.getenv('IAM_UPDATE_TIME')

        if not iam_token or not update_time:
            return None

        # Проверяем прошел ли час с момента последнего обновления
        last_update = datetime.fromisoformat(update_time)
        if datetime.now() - last_update > timedelta(hours=1):
            return None

        return iam_token

    except Exception as e:
        logging.error(f"Ошибка при проверке IAM токена: {e}")
        return None


def get_actual_iam():
    """Получение актуального IAM токена"""
    # Проверяем текущий токен
    current_iam = check_iam_token()
    if current_iam:
        logging.info("Используется текущий IAM токен")
        return current_iam

    # Если токен устарел или отсутствует, получаем новый
    try:
        load_dotenv()
        oauth_token = os.getenv('OAUTH')

        if not oauth_token:
            logging.error("OAuth токен не найден в .env файле")
            return None

        new_iam = get_iam_token(oauth_token)
        if new_iam and update_env_file(new_iam):
            logging.info("Получен и сохранен новый IAM токен")
            return new_iam

    except Exception as e:
        logging.error(f"Ошибка при получении актуального IAM токена: {e}")

    return None
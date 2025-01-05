# logo_generator.py
import random
import requests
import base64
import os
import time
from dotenv import load_dotenv
from iam_updater import get_actual_iam
import logging

logging.basicConfig(level=logging.INFO, filename='logo_generator.log', encoding='utf-8')

load_dotenv()


def generate_logo(style, description, filename):
    try:
        # Получаем актуальный IAM токен
        iam = get_actual_iam()
        if not iam:
            logging.error("Не удалось получить IAM токен")
            return False

        catalog_id = os.environ["CATALOG_ID"]
        model_url = os.environ["MODEL_URL"]
        image_url = os.environ["IMAGE_URL"]

        headers = {
            "Authorization": f"Bearer {iam}",
            "Content-Type": "application/json"
        }

        data = {
            "modelUri": f"art://{catalog_id}/yandex-art/latest",
            "generationOptions": {
                "seed": f"{random.randint(0, 1000000)}",
                "aspectRatio": {
                    "widthRatio": "1",
                    "heightRatio": "1"
                }
            },
            "messages": [
                {
                    "weight": "1",
                    "text": f"Создай простой векторный логотип. Стиль: {style}. Описание: {description}. Максимум 3 цвета, минимум деталей, белый фон, центрированная композиция. Логотип должен быть читаемым в малом размере."                }
            ]
        }

        get_id = requests.post(model_url, headers=headers, json=data)
        if get_id.status_code != 200:
            logging.error(f"Ошибка при получении ID: {get_id.text}")
            return False

        image_id = get_id.json()["id"]
        logging.info(f"Получен ID изображения: {image_id}")

        # Ждем генерацию
        time.sleep(10)

        get_image_url = f"{image_url}/{image_id}"
        get_image = requests.get(get_image_url, headers=headers)

        if get_image.status_code != 200:
            logging.error(f"Ошибка при получении изображения: {get_image.text}")
            return False

        # Получаем и сохраняем изображение
        image_base64 = get_image.json()['response']['image']
        image_data = base64.b64decode(image_base64)

        with open(filename, 'wb') as f:
            f.write(image_data)

        logging.info(f"Логотип успешно сохранен в файл: {filename}")
        return True

    except Exception as e:
        logging.error(f"Ошибка при генерации логотипа: {e}")
        return False
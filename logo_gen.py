import random
import requests
import base64
import os
import time
from dotenv import load_dotenv
from iam_updater import get_actual_iam

load_dotenv()


# Получаем актуальный IAM токен
iam = get_actual_iam()
if not iam:
    print("Не удалось получить IAM токен")
    exit(1)

catalog_id = os.environ["CATALOG_ID"]

model_url = os.environ["MODEL_URL"]
image_url = os.environ["IMAGE_URL"]

def generate_logo(style, description):
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
                "text": f"Нарисуй логотип под описание: {description}, в стиле: {style}, высокое качество"
            }
        ]
    }

    get_id = requests.post(model_url, headers=headers, json=data)
    if get_id.status_code == 200:
        image_id = get_id.json()["id"]
        print(image_id)
        time.sleep(10)

        get_image_url = f"{image_url}/{image_id}"
        get_image = requests.get(get_image_url, headers=headers)

        # Проверяем успешность запроса
        if get_image.status_code == 200:
            # Получаем base64 строку изображения
            image_base64 = get_image.json()['response']['image']

            # Декодируем base64 в бинарные данные
            image_data = base64.b64decode(image_base64)

            # Сохраняем в файл
            with open('image.jpeg', 'wb') as f:
                f.write(image_data)
        else:
            print(f"Ошибка: {get_image.status_code}")
            print(get_image.text)

    else:
        print(get_id.text)


generate_logo('Строгий', 'Нарисуем логотип с небольшим описанием для компании Рога и Копыта')
import random
from random import Random

import requests
import os
import img2pdf
from time import sleep

# ===== КОНФИГУРАЦИЯ =====
# ВАЖНО: ЗАПОЛНИТЕ ЭТИ ДАННЫЕ ПЕРЕД ЗАПУСКОМ

# Значение куки SID из вашего браузера после авторизации на litres.ru
SID_COOKIE_VALUE = ""  # Замените на ваше реальное значение! Например, "a1b2c3d4e5f6..."

# ID файла книги (берется из URL параметра file=)
FILE_ID = "11111111"  # Замените на нужный ID вашей книги

# Общее количество страниц для скачивания (нужно узнать или оценить)
TOTAL_PAGES = 1   # Начните с малого числа для теста, затем увеличьте

# Параметры качества из URL (обычно менять не нужно)
RT_PARAM = "w1900"  # Ширина/качество
FT_PARAM = "gif"   # Формат изображения. Можно попробовать "gif", но jpeg обычно меньше весит.

# Задержка между запросами в секундах (чтобы не нагружать сервер и избежать блокировки)
DELAY_BETWEEN_REQUESTS = 0.3

# Имя папки для сохранения изображений и итогового PDF
OUTPUT_FOLDER = "downloaded_book"
# ========================

def main():
    # Создаем папку для сохранения страниц, если её нет
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # Создаем сессию для сохранения кук между запросами
    session = requests.Session()
    session.cookies.set("SID", SID_COOKIE_VALUE, domain=".litres.ru")

    # Список для хранения путей к скачанным изображениям
    image_paths = []

    print("Начинаем скачивание страниц...")
    for page_num in range(1, TOTAL_PAGES + 1):
        # Формируем URL для запроса конкретной страницы
        url = f"https://www.litres.ru/pages/get_pdf_page/?file={FILE_ID}&page={page_num}&rt={RT_PARAM}&ft={FT_PARAM}"

        # Формируем имя файла для текущей страницы
        image_filename = os.path.join(OUTPUT_FOLDER, f"page_{page_num:04d}.{FT_PARAM}")
        image_paths.append(image_filename)

        # Если файл уже существует, пропускаем скачивание
        if os.path.exists(image_filename):
            print(f"Страница {page_num} уже существует, пропускаем.")
            continue

        # Отправляем GET-запрос с куками
        response = session.get(url, stream=True)  # stream=True для обработки больших файлов

        # Проверяем, успешен ли запрос
        if response.status_code == 200:
            # Сохраняем изображение в файл
            with open(image_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Успешно скачана страница {page_num} из {TOTAL_PAGES}")
        else:
            # Если страница не найдена (404) или другая ошибка, останавливаем цикл
            print(f"Ошибка при загрузке страницы {page_num}. Код ответа: {response.status_code}")
            print("Это может означать, что страниц в книге меньше, чем указано. Прерывание процесса.")
            # Удаляем пустой или ошибочный файл, если он был создан
            if os.path.exists(image_filename):
                os.remove(image_filename)
            break

        # Делаем небольшую паузу между запросами из вежливости к серверу
        sleep(DELAY_BETWEEN_REQUESTS)

    print("\nСкачивание страниц завершено. Начинаем создание PDF...")

    # Фильтруем список путей, оставляя только существующие файлы
    existing_image_paths = [path for path in image_paths if os.path.exists(path)]

    if not existing_image_paths:
        print("Нет скачанных изображений для создания PDF.")
        return

    # Сортируем файлы по имени (чтобы страницы были по порядку)
    existing_image_paths.sort()

    # Создаем имя для итогового PDF-файла
    pdf_filename = os.path.join(OUTPUT_FOLDER, f"book_{FILE_ID}.pdf")

    # Конвертируем все изображения в один PDF файл
    try:
        with open(pdf_filename, "wb") as pdf_file:
            pdf_file.write(img2pdf.convert(existing_image_paths))
        print(f"PDF-книга успешно создана: {pdf_filename}")
    except Exception as e:
        print(f"Произошла ошибка при создании PDF: {e}")

if __name__ == "__main__":
    main()
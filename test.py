from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

CHAT_URL = os.getenv("CHAT_URL")
FIRST_ELEMENT_XPATH = os.getenv("FIRST_ELEMENT_XPATH")
SECOND_ELEMENT_XPATH = os.getenv("SECOND_ELEMENT_XPATH")
THIRD_ELEMENT_XPATH = os.getenv("THIRD_ELEMENT_XPATH")

# Функция для кликов по элементам
def click_elements(driver):
    try:
        first_element = driver.find_element(By.XPATH, FIRST_ELEMENT_XPATH)
        first_element.click()
        print("Первый элемент найден и кликнут: Майнинг")
    except Exception as e:
        print(f"Ошибка при клике по первому элементу: {e}")
        return

    time.sleep(3)

    try:
        second_element = driver.find_element(By.XPATH, SECOND_ELEMENT_XPATH)
        second_element.click()
        print("Второй элемент найден и кликнут: Go to mining")
    except Exception as e:
        print(f"Ошибка при клике по второму элементу: {e}")
        return

    time.sleep(3)

    try:
        third_element = driver.find_element(By.XPATH, THIRD_ELEMENT_XPATH)
        third_element.click()
        print("Третий элемент найден и кликнут: claim")
    except Exception as e:
        print(f"Ошибка при клике по третьему элементу: {e}")
        return

# Функция для запуска Selenium и выполнения кликов
def main():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Автоматическая установка ChromeDriver с помощью webdriver_manager
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Открываем чат
    driver.get(CHAT_URL)

    # Выполняем клики по элементам
    click_elements(driver)

    # Оставляем браузер открытым для проверки
    time.sleep(60)
    driver.quit()

if __name__ == '__main__':
    main()

import pickle
import time
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from selenium import webdriver
from selenium.webdriver.common.by import By
import threading
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_URL = os.getenv("CHAT_URL")
FIRST_ELEMENT_XPATH = os.getenv("FIRST_ELEMENT_XPATH")
SECOND_ELEMENT_XPATH = os.getenv("SECOND_ELEMENT_XPATH")
THIRD_ELEMENT_XPATH = os.getenv("THIRD_ELEMENT_XPATH")
CLICK_INTERVAL = int(os.getenv("CLICK_INTERVAL"))

# Для хранения данных авторизации
user_data = {"phone": None, "code": None}


# Функция для запуска бота
def start_bot():
    def start(update: Update, context: CallbackContext):
        update.message.reply_text("Привет! Введи номер телефона для авторизации в формате +1234567890:")

    def handle_message(update: Update, context: CallbackContext):
        text = update.message.text

        # Если номер телефона ещё не сохранён
        if user_data["phone"] is None:
            user_data["phone"] = text
            update.message.reply_text("Номер телефона сохранен. Ждите код для авторизации.")
            print(f"Номер телефона: {text}")

        # Если телефон уже сохранён, обрабатываем как код авторизации
        elif user_data["code"] is None:
            user_data["code"] = text
            update.message.reply_text("Код авторизации сохранен.")
            print(f"Код авторизации: {text}")

    def main():
        updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        updater.start_polling()
        updater.idle()

    main()


# Функция для авторизации через Selenium
def start_selenium():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)

    # Проверка наличия cookies
    if os.path.exists("cookies.pkl"):
        driver.get('https://web.telegram.org')
        with open("cookies.pkl", "rb") as cookiesfile:
            cookies = pickle.load(cookiesfile)
            for cookie in cookies:
                driver.add_cookie(cookie)

        # Обновляем страницу после загрузки cookies
        driver.refresh()

        # Проверяем, авторизован ли пользователь
        time.sleep(5)  # Ждем загрузки страницы
        if "login" not in driver.current_url:
            print("Авторизация через cookies прошла успешно.")
            return driver
        else:
            print("Cookies недействительны, требуется повторная авторизация.")
    else:
        print("Cookies не найдены, требуется авторизация.")

    # Если cookies недействительны, выполняем авторизацию
    driver.get('https://web.telegram.org')

    # Ожидание ввода телефона и кода из бота
    while user_data["phone"] is None:
        print("Ожидание ввода номера телефона...")
        time.sleep(5)

    phone = user_data["phone"]

    # Ввод телефона в поле
    phone_input = driver.find_element(By.NAME, 'phone_number')
    phone_input.send_keys(phone)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()

    # Ожидание ввода кода
    while user_data["code"] is None:
        print("Ожидание ввода кода авторизации...")
        time.sleep(5)

    code = user_data["code"]

    time.sleep(5)  # Ожидание страницы для ввода кода

    # Ввод кода в поле
    code_input = driver.find_element(By.NAME, 'phone_code')
    code_input.send_keys(code)
    driver.find_element(By.XPATH, '//button[text()="Next"]').click()

    # Ожидание авторизации и сохранение cookies
    time.sleep(10)

    with open("cookies.pkl", "wb") as cookiesfile:
        pickle.dump(driver.get_cookies(), cookiesfile)
        print("Cookies сохранены.")

    return driver


# Функция для последовательного выполнения кликов по элементам
def click_elements(driver):
    # 1. Клик по первому элементу с текстом "Майнинг"
    try:
        first_element = driver.find_element(By.XPATH, FIRST_ELEMENT_XPATH)
        first_element.click()
        print("Первый элемент найден и кликнут: Майнинг")
    except Exception as e:
        print(f"Ошибка при клике по первому элементу: {e}")
        return

    time.sleep(3)  # Ждем загрузки новой страницы

    # 2. Клик по кнопке "Go to mining"
    try:
        second_element = driver.find_element(By.XPATH, SECOND_ELEMENT_XPATH)
        second_element.click()
        print("Второй элемент найден и кликнут: Go to mining")
    except Exception as e:
        print(f"Ошибка при клике по второму элементу: {e}")
        return

    time.sleep(3)  # Ждем загрузки новой страницы

    # 3. Клик по элементу "claim"
    try:
        third_element = driver.find_element(By.XPATH, THIRD_ELEMENT_XPATH)
        third_element.click()
        print("Третий элемент найден и кликнут: claim")
    except Exception as e:
        print(f"Ошибка при клике по третьему элементу: {e}")
        return


# Функция для выполнения периодических кликов
def click_periodically(driver, interval):
    while True:
        click_elements(driver)
        time.sleep(interval)


# Главная функция для запуска всего процесса
def main():
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()

    # Запускаем Selenium и пытаемся восстановить сессию через cookies
    driver = start_selenium()

    # Запуск функции периодических кликов
    click_periodically(driver, CLICK_INTERVAL)


if __name__ == '__main__':
    main()

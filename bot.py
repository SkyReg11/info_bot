import telebot
from telebot import types

from config import BOT_TOKEN
from services import CurrencyService, NewsService, WeatherService

# Инициализируем бота и сервисы
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
currency_service = CurrencyService()
weather_service = WeatherService()
news_service = NewsService()


def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    # Главное меню с кнопками
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_currency = types.KeyboardButton("💰 Курсы валют")
    btn_weather = types.KeyboardButton("🌤 Погода")
    btn_news = types.KeyboardButton("📰 Новости")
    keyboard.add(btn_currency, btn_weather, btn_news)
    return keyboard


@bot.message_handler(commands=["start", "help"])
def send_welcome(message: types.Message):
    text = (
        f"Привет, <b>{message.from_user.first_name}</b>! 👋\n"
        "Я твой личный бот-агрегатор. Выбери нужный раздел в меню ниже:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_main_keyboard())


@bot.message_handler(content_types=["text"])
def handle_menu(message: types.Message):
    if message.text == "💰 Курсы валют":
        bot.send_message(message.chat.id, "⏳ Загружаю курсы...")
        report = currency_service.get_rates()
        bot.send_message(message.chat.id, report)

    elif message.text == "🌤 Погода":
        # Спрашиваем город и передаем управление в следующую функцию
        msg = bot.send_message(message.chat.id, "🏙 Напишите название города:")
        bot.register_next_step_handler(msg, process_city_step)

    elif message.text == "📰 Новости":
        news = news_service.get_news()
        bot.send_message(message.chat.id, news)

    else:
        bot.send_message(
            message.chat.id,
            "Не понял команду. Пожалуйста, воспользуйтесь кнопками меню 👇",
            reply_markup=get_main_keyboard(),
        )


def process_city_step(message: types.Message):
    # Обрабатывает введенный пользователем город
    city = message.text.strip()
    weather_report = weather_service.get_weather(city)
    bot.send_message(message.chat.id, weather_report, reply_markup=get_main_keyboard())


if __name__ == "__main__":
    print("Бот запущен и готов к работе...")
    bot.infinity_polling()
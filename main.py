from background import keep_alive
from aiogram import Bot, Dispatcher, executor, types
import datetime
import requests
import json

OPEN_WEATHER_TOKEN = 'b142e3d9effdf086abc15456f2db13b6'
TG_BOT_TOKEN = '7008077074:AAEpoLUbfpNgHu7BzhNXUuDpKQSoXa5bqSo'

bot = Bot(TG_BOT_TOKEN)
dp = Dispatcher(bot)

weather_smile = {
    'Clear': '☀️',
    'Clouds': '⛅️',
    'Rain': '🌧',
    'Drizzle': '🌦',
    'Thunderstorm': '⛈',
    'Snow': '❄️',
    'Mist': '🌫',
}

temperature_smile = {
    'cold': '🥶',
    'comfort': '🙂',
    'hot': '🥵',
}

wind_smile = {
    'gentle': '🌬',
    'medium': '💨',
    'heavy': '🌪',
}


@dp.message_handler(commands=['start'])
async def info(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Получить прогноз погоды', callback_data='city'))
    markup.add(types.InlineKeyboardButton('Список команд', callback_data='list'))
    await message.answer('Привет, тут вы можете узнать прогноз погоды.', reply_markup=markup)


@dp.message_handler(commands=['listCity'])
async def reply(message: types.Message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(types.InlineKeyboardButton('Брест'))
    markup.add(types.InlineKeyboardButton('Витебск'))
    markup.add(types.InlineKeyboardButton('Гомель'))
    markup.add(types.InlineKeyboardButton('Гродно'))
    markup.add(types.InlineKeyboardButton('Минск'))
    markup.add(types.InlineKeyboardButton('Могилев'))
    await message.answer('Привет, тут ты можешь выбрать областной центр Беларуси, чтобы узнать там погоду.',
                         reply_markup=markup)


@dp.callback_query_handler()
async def callback(call):
    if call.data == 'list':
        await call.message.answer('/listCity\n/start')
    elif call.data == 'city':
        await call.message.answer('Введите город')


@dp.message_handler(content_types=['text'])
async def reply(message: types.Message):
    city = message.text.lower().strip()
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&lang=ru&appid={OPEN_WEATHER_TOKEN}&units=metric'
    result = requests.get(url)
    data = json.loads(result.text)
    if result.status_code == 200:
        current_temperature = data['main']['temp']
        feels_like_temperature = data['main']['feels_like']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind_speed = data['wind']['speed']
        wind_gust = data['wind']['gust']
        weather = data['weather'][0]['main']
        weather_description = data['weather'][0]['description']

        if weather in weather_smile:
            wheather_icon = weather_smile[weather]

        if current_temperature < 8:
            temperature_icon = temperature_smile['cold']
        elif 8 <= current_temperature <= 25:
            temperature_icon = temperature_smile['comfort']
        else:
            temperature_icon = temperature_smile['hot']

        if wind_speed < 10:
            wind_icon = wind_smile['gentle']
        elif 10 <= wind_speed <= 17:
            wind_icon = wind_smile['medium']
        else:
            wind_icon = wind_smile['heavy']

        await message.answer(f'👩‍💻👩‍💻👩‍💻{datetime.datetime.now().strftime("%d-%m-%Y %H:%M")}👩‍💻👩‍💻👩‍💻\n'
                             f'В городе {message.text} сейчас {weather_description} {wheather_icon}\n'
                             f'Температура {current_temperature} °C {temperature_icon}\n'
                             f'Ощущается как {feels_like_temperature} °C\n'
                             f'Скорость ветра {wind_speed} м/с с порывами до {wind_gust} м/с {wind_icon}\n'
                             f'Влажность {humidity}%\n'
                             f'Давление {pressure} мм.рт.ст\n')

    elif result.status_code == 404:
        await message.answer('Город не найден.')


keep_alive()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import telebot
from config import TOKEN
from utils import user
from telebot import types

bot = telebot.TeleBot(TOKEN)

user_profile = user.copy()

def start_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_connect = types.InlineKeyboardButton(text='Запрос на подключение', callback_data='start_connect')
    btn_application = types.InlineKeyboardButton(text='Оставить заявку', callback_data='start_application')
    keyboard.add(btn_connect, btn_application)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message : types.Message):
    bot.send_message(chat_id=message.chat.id, text='Добро пожаловать',reply_markup=start_keyboard())


def get_name(message):
    name = message.text
    user_profile['first_name'] = name
    bot.send_message(message.chat.id, f"Привет, {name}! Введите фамилию:")
    bot.register_next_step_handler(message, get_second_name)


def get_second_name(message: types.Message):
    second_name = message.text
    user_profile['second_name'] = second_name
    bot.send_message(chat_id=message.chat.id, text=f'{user_profile['first_name']}! Введите возраст:')
    bot.register_next_step_handler(message, get_age)


def get_age(message: types.Message):
    age = message.text
    user_profile['age'] = age
    bot.send_message(message.chat.id, f"{user_profile['first_name']}, введите почту:")
    bot.register_next_step_handler(message, get_email)


def get_email(message: types.Message):
    email = message.text
    user_profile['email'] = email
    bot.send_message(message.chat.id, f"{user_profile['first_name']}, введите город:")
    bot.register_next_step_handler(message, get_address_city)


def get_address_city(message: types.Message):
    city = message.text
    user_profile['address']['city'] = city
    bot.send_message(message.chat.id, f"{user_profile['first_name']}, введите улицу")
    bot.register_next_step_handler(message, get_address_street)


def get_address_street(message : types.Message):
    street = message.text
    user_profile['address']['street'] = street
    bot.send_message(message.chat.id, f"{user_profile['first_name']}. Введите дом")
    bot.register_next_step_handler(message, get_address_house)

def get_address_house(message : types.Message):
    house = message.text
    user_profile['address']['house'] = house
    bot.send_message(message.chat.id, f'{user_profile['first_name']}. Введите квартиру')
    bot.register_next_step_handler(message, get_address_flat)


def get_address_flat(message : types.Message):
    flat = message.text
    user_profile['address']['flat'] = flat
    bot.send_message(message.chat.id, f"Ваши данные успешно сохранены!")
    print(user_profile)

@bot.callback_query_handler(func=lambda callback : callback.data.startswith('start_'))
def start_callback_handler(callback : types.CallbackQuery):
    bot.answer_callback_query(callback.id)
    data = callback.data.replace('start_', '')
    if data == 'connect':
        bot.send_message(chat_id=callback.message.chat.id, text='Введите имя: ')
        bot.register_next_step_handler(callback.message, get_name)
    elif data == 'application':
        ...
bot.polling()

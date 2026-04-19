import telebot
from config import TOKEN
from utils import user
from telebot import types
import json
import os

bot = telebot.TeleBot(TOKEN)
file_name = 'users.json'
user_profile = user.copy()


def add_user(new_user):
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = []

    exists = any(user['id'] == new_user['id'] for user in users)
    if not exists:
        users.append(new_user)
        with open(file_name, mode='w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=4)


def check_user_availability(user_id):
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = []
    exists = any(user['id'] == user_id for user in users)
    return exists


def start_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_connect = types.InlineKeyboardButton(text='Стать абонентом', callback_data='start_connect')
    btn_application = types.InlineKeyboardButton(text='Я существующий абонент', callback_data='start_application')
    keyboard.add(btn_connect, btn_application)
    return keyboard


def keyboard_service_func():
    keyboard_service = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    btn_internet = types.KeyboardButton(text='Интернет')
    btn_television = types.KeyboardButton(text='Телевидение')
    btn_telephony = types.KeyboardButton(text='Телефония')
    btn_intercom = types.KeyboardButton(text='Домофония')
    btn_video_surveillance = types.KeyboardButton(text='Видеонаблюдение')
    keyboard_service.add(btn_internet, btn_television, btn_telephony, btn_intercom, btn_video_surveillance)
    return keyboard_service


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    user_profile['id'] = message.from_user.id
    print(message.from_user.id)
    bot.send_message(chat_id=message.chat.id, text='Вас приветствует компания Росинтел!', reply_markup=start_keyboard())


def choice_service(message):
    text = message.text
    if text not in ['Интернет', 'Телевидение', 'Телефония', 'Домофония', 'Видеонаблюдение']:
        bot.send_message(chat_id=message.chat.id, text='У нас нет такой услуги! Попробуйте ещё раз')
        bot.register_next_step_handler(message, choice_service)
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите имя: ')
        bot.register_next_step_handler(message, get_name)


def get_name(message):
    name: str = message.text
    if not name.isalpha():
        bot.send_message(message.chat.id, 'Введите правильно ваше имя!')
        bot.register_next_step_handler(message, get_name)
    else:
        name = name.title()
        user_profile['first_name'] = name
        bot.send_message(message.chat.id,
                         f"Привет, {name}! Введите номер телефона (без пробелов и специальных символов):")
        bot.register_next_step_handler(message, get_phone)


def get_phone(message):
    phone: str = message.text
    phone_num = phone[1:]
    if phone_num.isdigit() and phone[0] == '+' or phone[0] == '8':
        if len(phone) == 11 or len(phone) == 12:
            user_profile['phone'] = phone
            bot.send_message(chat_id=message.chat.id, text=f"{user_profile['first_name']}, введите город:")
            bot.register_next_step_handler(message, get_address_city)
        else:
            bot.send_message(chat_id=message.chat.id, text='Длина номера телефона не совпадает норме')
            bot.register_next_step_handler(message, get_phone)
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите номер телефона без пробелов и специальных символов')
        bot.register_next_step_handler(message, get_phone)


def get_address_city(message: types.Message):
    city = message.text
    if not city.isalpha():
        bot.send_message(message.chat.id, 'Введите правильно ваш город!')
        bot.register_next_step_handler(message, get_address_city)
    else:
        user_profile['address']['city'] = city
        bot.send_message(message.chat.id, f"{user_profile['first_name']}, введите улицу")
        bot.register_next_step_handler(message, get_address_street)


def get_address_street(message: types.Message):
    street = message.text
    if not street.isalpha():
        bot.send_message(message.chat.id, 'Введите правильно вашу улицу!')
        bot.register_next_step_handler(message, get_address_street)
    else:
        user_profile['address']['street'] = street
        bot.send_message(message.chat.id, f"{user_profile['first_name']}. Введите дом")
        bot.register_next_step_handler(message, get_address_house)


def get_address_house(message: types.Message):
    house = message.text
    user_profile['address']['house'] = house
    bot.send_message(message.chat.id, f'{user_profile['first_name']}. Введите квартиру')
    bot.register_next_step_handler(message, get_address_flat)


def get_address_flat(message: types.Message):
    flat = message.text
    if flat.isdigit():
        user_profile['address']['flat'] = flat
        bot.send_message(message.chat.id, f"Ваши данные успешно сохранены!")
        bot.send_message(message.chat.id, text=f'В скором времени наш оператор позвонит вам.')
        add_user(user_profile)
        print(user_profile)
    else:
        bot.send_message(chat_id=message.chat.id, text='Введите правильно свою квартиру')
        bot.register_next_step_handler(message, get_address_flat)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('start_'))
def start_callback_handler(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id)
    data = callback.data.replace('start_', '')
    print(data)
    print(callback.message.from_user.id)
    if data == 'connect':
        if check_user_availability(user_profile['id']):
            bot.send_message(chat_id=callback.message.chat.id, text='Вы уже зарегистрированы')
            print(111)

            return
        bot.send_message(chat_id=callback.message.chat.id, text='Выберите услугу:',
                         reply_markup=keyboard_service_func())
        bot.register_next_step_handler(callback.message, choice_service)
    elif data == 'application':
        ...


bot.polling()

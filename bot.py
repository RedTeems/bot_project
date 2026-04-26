import telebot


from config import TOKEN
from utils import user, service_type
from telebot import types
import json
import os

bot = telebot.TeleBot(TOKEN)
file_name = 'users.json'
services_file = 'services.json'
user_profile = user.copy()
is_service_type = False


def add_service(user_id, service):
    if os.path.exists(services_file):
        with open(services_file, mode='r', encoding='utf-8') as f:
            existing_service = json.load(f)
    else:
        existing_service = {}
    exists = False
    for user_id in existing_service:
        if service in existing_service[user_id]:
            exists = True
            break
    #exists = any(service in existing_service[user_id] for user_id in existing_service)
    if not exists:

        if existing_service and type(existing_service[str(user_id)]) == list:
            existing_service[str(user_id)].append(service)
        else:
            existing_service[user_id] = [service]

        with open(services_file, mode='w', encoding='utf-8') as f:
            json.dump(existing_service, f, ensure_ascii=False, indent=4)
            return True
    else:
        return False




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

def get_selected_service(user_id):
    if os.path.exists(services_file):
        with open(services_file, mode='r', encoding='utf-8') as f:
            existing_service = json.load(f)
    else:
        existing_service = {}
    if existing_service and existing_service[user_id] :
        res = (f'Ваши услуги: \n'
               f'{'\n'.join(existing_service[user_id])}')
        return res
    else:
        return 'У вас нет действующих услуг'



def check_user_availability(user_id):
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = []
    exists = any(user['id'] == user_id for user in users)
    return exists


def start_keyboard(register_user: str):
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    btn_connect = types.InlineKeyboardButton(text='Стать абонентом', callback_data='start_connect')
    btn_application = types.InlineKeyboardButton(text='Я существующий абонент', callback_data='start_application')
    if register_user == 'register':
        keyboard.add(btn_application)
    else:
        keyboard.add(btn_connect)
    return keyboard


def keyboard_service_func():
    keyboard_service = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=1)
    btn_internet = types.KeyboardButton(text=service_type[0])
    btn_television = types.KeyboardButton(text=service_type[1])
    btn_telephony = types.KeyboardButton(text=service_type[2])
    btn_intercom = types.KeyboardButton(text=service_type[3])
    btn_video_surveillance = types.KeyboardButton(text=service_type[4])
    keyboard_service.add(btn_internet, btn_television, btn_telephony, btn_intercom, btn_video_surveillance)
    return keyboard_service


def keyboard_auth_user_actions():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    btn_new_connection = types.InlineKeyboardButton(text='Новое подключение', callback_data='auth_new_connection')
    btn_selected_connection = types.InlineKeyboardButton(text='Ваши услуги', callback_data='auth_selected_connection')
    btn_support = types.InlineKeyboardButton(text='Техподдержка', url='https://t.me/Redflaut')
    btn_disabling = types.InlineKeyboardButton(text='Отключение услуги', callback_data='auth_disabling')
    btn_payment = types.InlineKeyboardButton(text='Оплата услуг', callback_data='auth_payment')
    keyboard.add(btn_new_connection, btn_selected_connection)
    keyboard.add(btn_support)
    keyboard.add(btn_disabling, btn_payment)
    return keyboard

def keyboard_disabling(user_id):
    if os.path.exists(services_file):
        with open(services_file, mode='r', encoding='utf-8') as f:
            existing_service = json.load(f)
    else:
        existing_service = {}
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    for i, btn in enumerate(existing_service[(str(user_id))]):
        callback_data = f'disabling_{i}_{btn}'
        button = types.InlineKeyboardButton(text=btn, callback_data=callback_data)
        keyboard.add(button)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message: types.Message):
    if os.path.exists(file_name):
        with open(file_name, mode='r', encoding='utf-8') as f:
            users = json.load(f)
    else:
        users = []
    if users:
        user_profile['id'] = str(message.from_user.id)
        print(user_profile['id'])
        is_register_user = False
        for user in users:
            print(user)
            if user_profile['id'] == user['id']:
                is_register_user = True
                break

        if is_register_user:
            bot.send_message(chat_id=message.chat.id, text='Вас приветствует компания Росинтел!',
                             reply_markup=start_keyboard('register'))
        else:
            bot.send_message(chat_id=message.chat.id, text='Вас приветствует компания Росинтел!',
                             reply_markup=start_keyboard('not_register'))


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
        bot.send_message(message.chat.id, text='Выберите действие:', reply_markup=keyboard_auth_user_actions())
        add_user(user_profile)

    else:
        bot.send_message(chat_id=message.chat.id, text='Введите правильно свою квартиру')
        bot.register_next_step_handler(message, get_address_flat)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('start_'))
def start_callback_handler(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id)
    data = callback.data.replace('start_', '')

    if data == 'connect':
        if check_user_availability(user_profile['id']):
            bot.send_message(chat_id=callback.message.chat.id, text='Вы уже зарегистрированы')

            return
        bot.send_message(chat_id=callback.message.chat.id, text='Введите ваше имя')
        bot.register_next_step_handler(callback.message, get_name)

    elif data == 'application':
        bot.send_message(callback.message.chat.id, text='Выберите действие:', reply_markup=keyboard_auth_user_actions())


@bot.callback_query_handler(func=lambda callback: callback.data.startswith('auth_'))
def auth_callback_handler(callback: types.CallbackQuery):
    global is_service_type
    bot.answer_callback_query(callback.id)
    data = callback.data.replace('auth_', '')
    if data == 'new_connection':
        bot.send_message(chat_id=callback.message.chat.id, text='Выберите услугу:',
                         reply_markup=keyboard_service_func())
        is_service_type = True

    elif data == 'selected_connection':

        user_id = user_profile['id']
        selected_service = get_selected_service(user_id)
        bot.send_message(chat_id=callback.message.chat.id, text=selected_service)



    elif data == 'disabling':
        bot.send_message(chat_id=callback.message.chat.id, text='Выберете услугу, которую хотите отключить:', reply_markup=keyboard_disabling(user_profile['id']))
    elif data == 'payment':
        ...


@bot.callback_query_handler(func= lambda callback: callback.data.startswith('disabling_'))
def disabling_handler(callback: types.CallbackQuery):
    bot.answer_callback_query(callback.id)
    _, idx, name = callback.data.split('_')


    if os.path.exists(services_file):
        with open(services_file, mode='r', encoding='utf-8') as f:
            existing_service = json.load(f)
    else:
        existing_service = {}
    if existing_service:
        for user_id in existing_service:
            if user_id == str(user_profile['id']):
                existing_service[user_id].remove(name)
                with open(services_file, mode='w', encoding='utf-8') as f:
                    json.dump(existing_service, f, ensure_ascii=False, indent=4)
                bot.send_message(chat_id=callback.message.chat.id, text='Услуга отключена')






@bot.message_handler(func=lambda message: message.text in service_type and is_service_type)
def service_type_handler(message: types.Message):
    global is_service_type
    service = message.text
    user_id = user_profile['id']
    is_success = add_service(user_id, service)
    is_service_type = False
    if is_success:
        bot.send_message(chat_id=message.chat.id, text='Услуга добавлена')

    else:
        bot.send_message(chat_id=message.chat.id, text='Услуга уже добавлена')


bot.polling()

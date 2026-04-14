# -*- coding: utf-8 -*-

"""
telegram bot for adding logo on photos and videos with register_next_step handler.
"""

import telebot #pip install pyTelegramBotAPI
from telebot import types
from pathlib import Path
import datetime
import logging
import subprocess
import transcribe_openai_chunks
import pymysql
import os
import glob
import configparser


logging.basicConfig(filename='transcriber_bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# API_TOKEN = os.environ.get('AUDIOOPENAI')
API_TOKEN = '2073537137:AAESpDgrCAOIDLYClFtG3-zc5LAl6baZS9k' #test bot
print(API_TOKEN)
bot = telebot.TeleBot(API_TOKEN)

user_dict = {}

class User: #get user data
    def __init__(self, id):
        self.id = id #string for the header
        self.firstname = None #string for the main text
        self.username = None #string for the main text



print("Listening...")
logging.info("Listening...")

# Define menu structure
menu = {
    'main': [
        ['Почати транскрибування / Start transcribing', 'option1'],
        ['Перевірити доступні хвилин / Check available minutes', 'option2'],
        ['Розмір донатів / Donations', 'option3'],
        ['Як користуватись ботом / How to use the bot', 'option4'],
        ['Back', 'menu']
    ]
    # ,
    # 'submenu1': [
    #     ['Закиньте сюди json файл', 'option1'],
    #     ['Option 2', 'option2'],
    #     ['Back', 'main']
    # ],
    # 'submenu2': [
    #     ['Закиньте сюди таблиці', 'option3'],
    #     ['Option 4', 'option4'],
    #     ['Back', 'main']
    # ]
}

def get_db_config(config_path=os.path.expanduser('~/.bots.cnf')):
    config = configparser.ConfigParser()
    config.read(config_path)

    # Extract credentials from the 'client' section.
    # Using .get() allows you to provide fallback values if needed.
    db_config = {
        'host': config.get('client', 'host'),
        'user': config.get('client', 'user'),
        'password': config.get('client', 'password'),
        'db': config.get('client', 'database'),
        'charset': 'utf8'
    }
    return db_config


def connectDB(request):

    db_config = get_db_config()
    # Use unpacking to pass the configuration as keyword arguments
    conn = pymysql.connect(**db_config)

    cur = conn.cursor()
    cur.execute('USE transcriber')
    print(request)
    cur.execute(request)
    data = cur.fetchone()[0]

    cur.close()
    conn.close()
    return data

def make_keyboard(menu_name):
    markup = types.InlineKeyboardMarkup()
    for btn_text, callback_data in menu[menu_name]:
        button = types.InlineKeyboardButton(btn_text, callback_data=callback_data)
        markup.add(button)
    return markup

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'option1':
        transcribe(call.message) #calling function
    elif call.data == 'option2':
        checkMinutes(call.message) #calling function
    elif call.data == 'option3':
        conditions(call.message) #calling function
    elif call.data == 'option4':
        donate(call.message) #calling function
    elif call.data in menu:
        bot.edit_message_text('You are in a submenu:', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=make_keyboard(call.data))
    else:
        bot.answer_callback_query(call.id, f"You chose {call.data}")

def request_phone_number(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    phone_button = telebot.types.KeyboardButton("Будь ласка, надайте ваш номер телефону для підключення", request_contact=True)
    markup.add(phone_button)

    # bot.send_message(message.chat.id, "Будь ласка, надайте ваш номер телефону:", reply_markup=markup)

#who is on duty today
def selectUser():
    # declaring user, who is on duty
    target_chat_ids = [{'@alona_ptk': '650797454'}, {'@alesia215': '521797754'},
                       {'@oksanaorsach': '765494993'}, {'@sandra_hudoznik5': '943675970'}]
    current_datetime = datetime.datetime.now()
    week_number = (current_datetime.day - 1) // 7 + 1
    if week_number <= len(target_chat_ids):
        user_info = target_chat_ids[week_number - 1]
        for username, chat_id in user_info.items():
            print(f'the week is {week_number} and on duty {username, chat_id}')
            logging.info(f'the week is {week_number} and on duty {username, chat_id}')
            return username, chat_id



@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Привіт! Я бот проекту nikcenter.org для розшифровки аудіо (будь-яка мова) та відеофайлів.\n
Наразі ми оновили бот - крім текста, він дає файл з таймкодом (доступний з 10 до 22:00).\n
Вибери, що потрібно в меню\n
--------------------------\n
Hello! I am an updated bot of the nikcenter.org project to transcribe audio (any language) and video files using AI chatGPT.\n
Choose what you need from the menu\n""", reply_markup=make_keyboard('main'))
    user_id = message.chat.id
    firstname = message.from_user.first_name  # getting name of user
    username = message.from_user.username  # getting name of username

    user = User(message.chat.id)  # initialize class User
    user_dict[message.chat.id] = user
    user.id = user_id
    user.firstname = firstname  # writting to class User
    user.username = username  # writting to class User
    phone_number = request_phone_number(message)
    print(f"User with id{user_id} and firstname {firstname} and username {username} "
          f"and {phone_number} tried to get access")
    logging.info(f"User with id {user_id} and firstname {firstname} and username {username} "
                  f"and {phone_number} tried to get access")



@bot.message_handler(content_types=['contact'])
def handle_contact_message(message):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    firstname = message.from_user.first_name
    username = message.from_user.username
    print(f"User with id{user_id} and firstname {firstname} and username {username} "
          f"and phone number {phone_number} into system")
    logging.info(f"User with id {user_id} and firstname {firstname} and username {username} "
                  f"and phone number {phone_number} into system")
    return phone_number
    # Do something with the phone number

def transcribe(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(user.id, user.username, user.firstname)
    bot.send_message(chat_id, f'Закиньте сюди аудіо файл розміром до 20 Мб.'
                              f'Якщо файл більший, то завантажьте на Dropbox і дайте лінк (для юзерів 2-го рівня)')


    @bot.message_handler(content_types=['audio'])
    def audio(message):
        try:
            chat_id = message.chat.id  # getting user id
            user_id = message.from_user.id
            firstname = message.from_user.first_name
            print(f"User has chat ID {chat_id} and user ID {user_id}")
            logging.info(f"User has chat ID {chat_id} and user ID {user_id}")
            # blacklistUsers(chat_id, user_id, firstname) #firewall
            whitelistUsers(chat_id, user_id, firstname)  # firewall
            directory, TIMESTAMP = makeFolder(message, chat_id)
            bot.send_message(chat_id, f'Файл отримано, треба почекати.\n'
                                      f'Розшифрування може зайняти 1/10 часу від загальної тривалості аудіо')
            """Downloading audio"""
            print('message.audio =', message.audio)
            fileID = message.audio.file_id
            fileName = message.audio.file_name
            print('fileID, fileName =', fileID, fileName)
            logging.info('fileID, fileName =', fileID, fileName)
            file_info = bot.get_file(fileID)
            print('file.file_path =', file_info.file_path)
            logging.info('file.file_path =', file_info.file_path)
            downloaded_file = bot.download_file(file_info.file_path)
            # filename = f"{directory}/audio_{TIMESTAMP}.wav"
            filename = f"{directory}/{fileName}"
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)
            print(filename, directory, TIMESTAMP)
            logging.info(filename, directory, TIMESTAMP)
            finalRes(chat_id, filename, directory, TIMESTAMP)
        except Exception as e:
            print(f"Audio upload  failed {e}")
            logging.info(f"Audio upload failed {e}")
            bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше. '
                                      f'\nМожливо, ви завантажуєте файл більший за 20МБ (20 000 000 байт).'
                                      f'\nВ цьому разі Вам потрібно підключти Dropbox.')

    @bot.message_handler(regexp="dropbox")  # handle link with dropbox
    def handle_message(message):
        chat_id = message.chat.id  # getting user id
        user_id = message.from_user.id
        firstname = message.from_user.first_name
        premListUsers(chat_id, user_id, firstname)  # firewall
        directory, TIMESTAMP = makeFolder(message, chat_id)
        print(f'Getting data from class {user_dict[chat_id].username}')
        logging.info(f'Getting data from class {user_dict[chat_id].username}')
        print(f'Getting data from class {user_dict[chat_id].id}')
        logging.info(f'Getting data from class {user_dict[chat_id].id}')
        print(f'Getting data from class {user_dict[chat_id].firstname}')
        logging.info(f'Getting data from class {user_dict[chat_id].firstname}')
        # logging.info(f'Bot sending filename to {user.firstname}')
        fileUrl = message.text
        bot.send_message(chat_id, f'Файл отримано, треба почекати.\n'
                                  f'Розшифрування може зайняти 1/10 часу від загальної тривалості аудіо')
        # Download filename
        print(
            f'Dropbox filename is downloadeding {fileUrl} for {user_dict[chat_id].id} {user_dict[chat_id].firstname} {user_dict[chat_id].username}')
        logging.info(
            f'Dropbox filename is downloadeding {fileUrl} for {user_dict[chat_id].id} {user_dict[chat_id].firstname} {user_dict[chat_id].username}')
        try:
            subprocess.call(['bash', 'downloadDrop.sh', fileUrl, directory, TIMESTAMP])

            filename = glob.glob(f"{directory}/audio_file_{TIMESTAMP}.*")
            print(f"Get file... {filename}")
            finalRes(chat_id, filename[0], directory, TIMESTAMP)
        except Exception as e:
            print(f"dropbox failed {e}")
            logging.info(f"dropbox failed {e}")
            bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')

def conditions(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(f'Reading conditions by {user.id, user.username, user.firstname}')
    logging.info(f'Reading conditions by {user.id, user.username, user.firstname}')
    bot.send_message(chat_id, f'Вітаю, {user.firstname}! Зараз ми надаємо доступ за такий донат:\n'
                              f'59	грн -	100	хв (без Дропбоксу до 20 мб)\n'
                              f'109	грн -	200	хв (без Дропбоксу)\n'
                              f'150	грн -	300	хв (без Дропбоксу)\n'
                              f'200	грн -	400	хв (з Дропбоксом для файлів понад 20 мб)\n'
                              f'250	грн -	500	хв (з Дропбоксом)\n'
                              f'460	грн -	1000 хв (з Дропбоксом)\n'
                              f'900	грн -	2000 хв (з Дропбоксом)\n')

def checkMinutes(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(f'Checking minutes for {user.id, user.username, user.firstname}')
    logging.info(f'Checking minutes for {user.id, user.username, user.firstname}')
    request = f'SELECT Available FROM users WHERE userID={chat_id}'
    try:
        available = connectDB(request)
        print(f'available {available}')
        bot.send_message(chat_id, f'На балансі є... {available} хвилин')
    except TypeError:
        print(f'available - None')
        bot.send_message(chat_id, f'У вас немає доступних хвилин'
                                  f'\nБудь ласка зробіть донат, і ми Вас підключемо до бота')

def donate(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    target_chat_id = selectUser()  # who is on duty today
    target_chat_id = ['@alesia215', '521797754']   # who is on duty today
    print(f'User {user.id, user.username, user.firstname} is trying to donate')
    logging.info(f'User {user.id, user.username, user.firstname} is trying to donate')
    bot.send_message(chat_id, f'Зробіть донат за реквізитами: \n'
                              f'Картка Приват - 5169360006139723 або банка Моно: https://send.monobank.ua/jar/2DxPtEsHnF\n'
                              f'Після цього завантажте прямо сюди квитанцію та повідомте юзеру {target_chat_id[0]} про донат.\n'
                              f'Протягом години ми надамо Вам доступ')

    @bot.message_handler(content_types=['document', 'photo'])
    def handle_document(message):
        TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # with miliseconds
        chat_id = message.chat.id  # getting user id
        user = user_dict[chat_id]
        print(f'User {user.id, user.username, user.firstname} uploaded doc in donation')
        logging.info(f'User {user.id, user.username, user.firstname} uploaded doc in donation')
        # Get the chat ID of the user you want to forward the document to
        # Replace 'ANOTHER_USER_CHAT_ID' with the actual chat ID of the user
        target_chat_id = selectUser() #who is on duty today
        directory = 'payment'
        if message.document:
            print('Getting message.document =', message.document)
            logging.info('Getting message.document =', message.document)

            fileID = message.document.file_id
            fileName = message.document.file_name
            print('fileID, fileName =', fileID, fileName)
            logging.info('fileID, fileName =', fileID, fileName)
            file_info = bot.get_file(fileID)
            print('file.file_path =', file_info.file_path)
            logging.info('file.file_path =', file_info.file_path)
            downloaded_file = bot.download_file(file_info.file_path)
            filename = f"{directory}/{fileName}"

        elif message.photo:
            print('Getting message.photo =', message.photo[-1])
            logging.info('Getting message.photo =', message.photo[-1])
            """Downloading photo"""
            print('message.photo =', message.photo)
            fileID = message.photo[-1].file_id
            print('fileID =', fileID)
            logging.info('fileID =', fileID)
            file_info = bot.get_file(fileID)
            print('file.file_path =', file_info.file_path)
            logging.info('file.file_path =', file_info.file_path)
            downloaded_file = bot.download_file(file_info.file_path)
            filename = f"{directory}/donation_{chat_id}_{TIMESTAMP}.jpg"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)

        file = open(filename, 'rb')
        # Forward the document to the target user
        bot.send_document(959676595, file)
        bot.send_document(target_chat_id[1], file)
        bot.send_message(target_chat_id[1], f'Юзер {user.id, user.username, user.firstname} пробує підключитися')


def whitelistUsers(chat_id, user_id, firstname):
    request = f'SELECT Level FROM users WHERE userID={chat_id}'
    level = connectDB(request)
    print(f"User with chat ID {chat_id} and user ID {user_id} has access level {level}")
    if level == 1 or level == 2:
        print(f'User with chat ID {chat_id} and user ID {user_id} in white list')
        logging.info(f'User with chat ID {chat_id} and user ID {user_id} in white list')
        pass
    else:
        deadEnd(chat_id, user_id, firstname)

def premListUsers(chat_id, user_id, firstname):
    request = f'SELECT Level FROM users WHERE userID={chat_id}'
    level = connectDB(request)
    print(f"User with chat ID {chat_id} and user ID {user_id} has access level {level}")
    if level == 2:
        print(f'User with chat ID {chat_id} and user ID {user_id} in prem list')
        logging.info(f'User with chat ID {chat_id} and user ID {user_id} in prem list')
        pass
    else:
        deadEnd(chat_id, user_id, firstname)

def deadEnd(chat_id, user_id, firstname):
    bot.send_message(chat_id, """Дякую, що звернулись до нас, але, на жаль,  у вас немає доступу цього рівня.
    Зайдіть у меню та зробіть донат""")
    print(f"User with chat ID {chat_id} and user ID {user_id} amd first name {firstname} has been blocked")
    logging.info(f"User with chat ID {chat_id} and user ID {user_id} amd first name {firstname} has been blocked")
    bot.ban_chat_member(chat_id, user_id)

def makeFolder(message, chat_id):
    """Prepairing folder"""
    firstname = message.from_user.first_name  # getting name of user
    username = message.from_user.username  # getting name of username
    user = User(chat_id)  # initialize class User
    user_dict[chat_id] = user
    user.firstname = firstname  # writting to class User
    user.username = username  # writting to class User
    print(f'id: {user.id}, name: {user.firstname}, username: {user.username}')
    logging.info(f'id: {user}, name: {user.firstname}, username: {user.username}')
    """Prepairing directory with chat_id and output file with timestamp"""
    TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # with miliseconds
    directory = f'dir_{chat_id}_{firstname}_{username}'
    print(f'Directory: {directory}')
    logging.info(f'Directory: {directory}')
    Path(directory).mkdir(exist_ok=True)  # creating a new directory if not exist
    print(f'Directory is made... {directory}')
    logging.info(f'Directory is made... {directory}')
    return directory, TIMESTAMP



def finalRes(chat_id, filename, directory, TIMESTAMP):
    newFile = f"{directory}/audio_{TIMESTAMP}.mp3"
    try:
        print(f"Start converting {filename} to {newFile} for {chat_id}")
        logging.info(f"Start converting {filename} to {newFile}")
        subprocess.call(['bash', 'audioConvert.sh', filename, newFile, str(chat_id)])
    except Exception as e:
        print(f"something wrong with the conversion. {e}")
        logging.info(f"something wrong with the conversion. {e}")
        bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')
    try:
        transcribe_openai_chunks.main(newFile, directory, TIMESTAMP)
    except Exception as e:
        print(f"something wrong with the conversion. {e}")
        logging.info(f"something wrong with the conversion. {e}")
        bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')
    output_file = f'./{directory}/audio_{TIMESTAMP}.txt'
    output_file_timecodes = f'./{directory}/audio_{TIMESTAMP}_timecodes.txt'
    file = open(output_file, 'rb')
    print(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    logging.info(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    bot.send_document(chat_id, file)  # sending file to user
    if os.path.exists(output_file_timecodes):
        file_timecodes = open(output_file_timecodes, 'rb')
        bot.send_document(chat_id, file_timecodes)
    bot.send_message(chat_id, 'Тримайте текст. Колеги, будь ласка, якщо вам подобається цей бот,'
                              '\nподякуйте і тегніте нашу сторінку в ФБ'
                              '\nhttps://www.facebook.com/nikcenter'
                              '\n')  # bot replying for a certain message

    # os.remove(filename)
    # os.remove(newFile)
    print(f"Files {filename}, {newFile} were removed")
    logging.info(f"Files {filename}, {newFile} were removed")
    """End of program"""



bot.infinity_polling()

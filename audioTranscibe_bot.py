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

logging.basicConfig(filename='transcriber_bot.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#TODO connect DB
#TODO replace white and prem list with
#TODO minutes left after transcribing



# API_TOKEN = os.environ.get('AUDIOOPENAI')
API_TOKEN = '2073537137:AAESpDgrCAOIDLYClFtG3-zc5LAl6baZS9k'
print(API_TOKEN)
bot = telebot.TeleBot(API_TOKEN)

user_dict = {}

class User: #get user data
    def __init__(self, id):
        self.id = id #string for the header
        self.firstname = None #string for the main text
        self.username = None #string for the main text



print("Listening...")
logging.debug("Listening...")

# Define menu structure
menu = {
    'main': [
        ['Почати транскрибування', 'option1'],
        ['Перевірити кількість доступних хвилин', 'option2'],
        ['Внести пожертву', 'option3'],
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
def connectDB(request):
    db_host = '127.0.0.1'
    conn = pymysql.connect(
        user='bots',
        host='localhost',
        passwd='editor46',
        db='transcriber', charset='utf8'
    )
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
        combine(call.message) #calling function
    elif call.data in menu:
        bot.edit_message_text('You are in a submenu:', chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=make_keyboard(call.data))
    else:
        bot.answer_callback_query(call.id, f"You chose {call.data}")
def request_phone_number(message):
    markup = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    phone_button = telebot.types.KeyboardButton("Будь ласка, надайте ваш номер телефону для підключення", request_contact=True)
    markup.add(phone_button)

    bot.send_message(message.chat.id, "Будь ласка, надайте ваш номер телефону:", reply_markup=markup)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.send_message(message.chat.id, """\
Привіт! Я бот проекту nikcenter.org для розшифровки аудіо та відеофайлів за допомогою AI chatGPT.\n
Вибери, що потрібно в меню:""", reply_markup=make_keyboard('main'))
    request = 'SELECT * FROM users'
    respond = connectDB(request)
    print(respond)
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
    logging.debug(f"User with id {user_id} and firstname {firstname} and username {username} "
                  f"and {phone_number} tried to get access")



@bot.message_handler(content_types=['contact'])
def handle_contact_message(message):
    phone_number = message.contact.phone_number
    user_id = message.from_user.id
    firstname = message.from_user.first_name
    username = message.from_user.username
    print(f"User with id{user_id} and firstname {firstname} and username {username} "
          f"and phone number {phone_number} into system")
    logging.debug(f"User with id {user_id} and firstname {firstname} and username {username} "
                  f"and phone number {phone_number} into system")
    return phone_number
    # Do something with the phone number

def transcribe(message):
    chat_id = message.chat.id  # getting user id
    user = user_dict[chat_id]
    print(user.id, user.username, user.firstname)
    bot.send_message(chat_id, f'Якщо ви отримали доступ, то закиньте сюди аудіо файл розміром до 20 Мб.'
                              f'Для юзерів, якій мають 4-й та 5-й рівень доступу можно закинути файл на дропбокс.')


    @bot.message_handler(content_types=['audio'])
    def audio(message):
        chat_id = message.chat.id  # getting user id
        user_id = message.from_user.id
        firstname = message.from_user.first_name
        print(f"User has chat ID {chat_id} and user ID {user_id}")
        logging.debug(f"User has chat ID {chat_id} and user ID {user_id}")
        # blacklistUsers(chat_id, user_id, firstname) #firewall
        whitelistUsers(chat_id, user_id, firstname)  # firewall
        directory, TIMESTAMP = makeFolder(message, chat_id)
        """Downloading audio"""
        print('message.audio =', message.audio)
        fileID = message.audio.file_id
        fileName = message.audio.file_name
        print('fileID, fileName =', fileID, fileName)
        logging.debug('fileID, fileName =', fileID, fileName)
        file_info = bot.get_file(fileID)
        print('file.file_path =', file_info.file_path)
        logging.debug('file.file_path =', file_info.file_path)
        downloaded_file = bot.download_file(file_info.file_path)
        # filename = f"{directory}/audio_{TIMESTAMP}.wav"
        filename = f"{directory}/{fileName}"
        with open(filename, 'wb') as new_file:
            new_file.write(downloaded_file)
        print(filename, directory, TIMESTAMP)
        logging.debug(filename, directory, TIMESTAMP)
        finalRes(chat_id, filename, directory, TIMESTAMP)

    @bot.message_handler(regexp="dropbox")  # handle link with dropbox
    def handle_message(message):
        chat_id = message.chat.id  # getting user id
        user_id = message.from_user.id
        firstname = message.from_user.first_name
        premListUsers(chat_id, user_id, firstname)  # firewall
        directory, TIMESTAMP = makeFolder(message, chat_id)
        print(f'Getting data from class {user_dict[chat_id].username}')
        logging.debug(f'Getting data from class {user_dict[chat_id].username}')
        print(f'Getting data from class {user_dict[chat_id].id}')
        logging.debug(f'Getting data from class {user_dict[chat_id].id}')
        print(f'Getting data from class {user_dict[chat_id].firstname}')
        logging.debug(f'Getting data from class {user_dict[chat_id].firstname}')
        # logging.debug(f'Bot sending filename to {user.firstname}')
        fileUrl = message.text

        # Download filename
        print(
            f'Dropbox filename is downloadeding {fileUrl} for {user_dict[chat_id].id} {user_dict[chat_id].firstname} {user_dict[chat_id].username}')
        logging.debug(
            f'Dropbox filename is downloadeding {fileUrl} for {user_dict[chat_id].id} {user_dict[chat_id].firstname} {user_dict[chat_id].username}')
        try:
            subprocess.call(['bash', 'downloadDrop.sh', fileUrl, directory, TIMESTAMP])

            filename = glob.glob(f"{directory}/audio_file_{TIMESTAMP}.*")
            print(f"Get file... {filename}")
            finalRes(chat_id, filename[0], directory, TIMESTAMP)
        except Exception as e:
            print(f"dropbox failed {e}")
            logging.debug(f"dropbox failed {e}")
            bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')

def whitelistUsers(chat_id, user_id, firstname):
    request = f'SELECT Level FROM users WHERE userID={chat_id}'
    level = connectDB(request)
    print(f"User with chat ID {chat_id} and user ID {user_id} has access level {level}")
    if level == 1 or level == 2:
        print(f'User with chat ID {chat_id} and user ID {user_id} in white list')
        logging.debug(f'User with chat ID {chat_id} and user ID {user_id} in white list')
        pass
    else:
        deadEnd(chat_id, user_id, firstname)

def premListUsers(chat_id, user_id, firstname):
    request = f'SELECT Level FROM users WHERE userID={chat_id}'
    level = connectDB(request)
    print(f"User with chat ID {chat_id} and user ID {user_id} has access level {level}")
    if level == 2:
        print(f'User with chat ID {chat_id} and user ID {user_id} in prem list')
        logging.debug(f'User with chat ID {chat_id} and user ID {user_id} in prem list')
        pass
    else:
        deadEnd(chat_id, user_id, firstname)

def deadEnd(chat_id, user_id, firstname):
    bot.send_message(chat_id, """Дякую, що звернулись до нас, але, на жаль,  у вас немає доступу цього рівня.
    Напишіть нам у Фейсбук: https://www.facebook.com/nikcenter, хто ви і для чого потребуєте допомоги бота.""")
    print(f"User with chat ID {chat_id} and user ID {user_id} amd first name {firstname} has been blocked")
    logging.debug(f"User with chat ID {chat_id} and user ID {user_id} amd first name {firstname} has been blocked")
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
    logging.debug(f'id: {user}, name: {user.firstname}, username: {user.username}')
    """Prepairing directory with chat_id and output file with timestamp"""
    TIMESTAMP = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]  # with miliseconds
    directory = f'dir_{chat_id}_{firstname}_{username}'
    print(f'Directory: {directory}')
    logging.debug(f'Directory: {directory}')
    Path(directory).mkdir(exist_ok=True)  # creating a new directory if not exist
    print(f'Directory is made... {directory}')
    logging.debug(f'Directory is made... {directory}')
    return directory, TIMESTAMP



def finalRes(chat_id, filename, directory, TIMESTAMP):
    newFile = f"{directory}/audio_{TIMESTAMP}.mp3"
    try:
        print(f"Start converting {filename} to {newFile} for {chat_id}")
        logging.debug(f"Start converting {filename} to {newFile}")
        subprocess.call(['bash', 'audioConvert.sh', filename, newFile, str(chat_id)])
    except Exception as e:
        print(f"something wrong with the conversion. {e}")
        logging.debug(f"something wrong with the conversion. {e}")
        bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')
    try:
        transcribe_openai_chunks.main(newFile, directory, TIMESTAMP)
    except Exception as e:
        print(f"something wrong with the conversion. {e}")
        logging.debug(f"something wrong with the conversion. {e}")
        bot.send_message(chat_id, f'Щось пішло не так. Спробуйте пізніше')
    output_file = f'./{directory}/audio_{TIMESTAMP}.txt'
    file = open(output_file, 'rb')
    print(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    logging.debug(f'Bot sending file to {user_dict[chat_id].firstname} {user_dict[chat_id].id} {user_dict[chat_id].username}')
    bot.send_document(chat_id, file)  # sending file to user
    bot.send_message(chat_id, 'Тримайте текст. Колеги, будь ласка, якщо вам подобається цей бот,'
                              '\nподякуйте і тегніте нашу сторінку в ФБ'
                              '\nhttps://www.facebook.com/nikcenter'
                              '\n')  # bot replying for a certain message

    # os.remove(filename)
    # os.remove(newFile)
    print(f"Files {filename}, {newFile} were removed")
    logging.debug(f"Files {filename}, {newFile} were removed")
    """End of program"""



bot.infinity_polling()

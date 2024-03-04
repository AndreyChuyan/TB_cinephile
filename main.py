import os
import json
import logging
from src.my_loguru import Logger
import telebot
from telebot import types
import requests
from config import TOKEN_TELEGRAM, TOKEN_OPENAI, http_proxy, https_proxy
from openai import OpenAI

# относительные пути поддиректорий
script_dir = os.path.dirname(os.path.abspath(__file__))
# Путь к директории, где будет храниться база данных
file_db = "db.json"
dir_db = "db"
dir_path_db = os.path.join(script_dir, dir_db)
DB_PATH = os.path.join(dir_path_db, file_db)

# прокси
import os
os.environ['http_proxy'] = http_proxy
os.environ['https_proxy'] = https_proxy

#создаем экземпляры
bot = telebot.TeleBot(TOKEN_TELEGRAM)
client = OpenAI(api_key=TOKEN_OPENAI)


# простые функции
# индексация строк
def split_words_with_index(items_list):
    result = []
    for index, item in enumerate(items_list, start=1):
        words = item.split(",")
        for i, word in enumerate(words, start=1):
            data = (f"{index} - {word}")
            result.append(data)
    return "\n".join(result)

            
def split_words(items_list):
    my_string = ' '.join(items_list)
    return my_string
    
# AI
def question_ai(message):
    '''Функция взаимодействия с AI'''
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
        model="gpt-3.5-turbo",
    )
    result = completion.choices[0].message.content
    return result            
            

class User:
    def __init__(self, user_id, favorite_books, favorite_genre, ignored_books):
        self.user_id = user_id
        self.favorite_books = favorite_books
        self.favorite_genre = favorite_genre
        self.ignored_books = ignored_books

class Database:
    def __init__(self):
        self.data = []      #список пользователей   

    def save_to_json(self):
        '''сохранение в БД'''
        with open(DB_PATH, 'w', encoding='utf-8') as file:
            json.dump([vars(data_block) for data_block in self.data], file, ensure_ascii=False, indent=4)

    def load_from_json(self):
        '''извлечение из БД'''
        try:
            with open(DB_PATH, 'r', encoding='utf-8') as file:
                data_db = json.load(file)
                self.data = [User(**data) for data in data_db]
        except FileNotFoundError:
            print("Не загружены данные: Файл базы данных не найден.") 

    def generate_report(self, user_id):
        '''печать отчета по пользователю'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                print(f"[ОТЧЕТ] ")
                print(f"Пользователь id: {data_block.user_id}")
                print(f"Любимые книги: {data_block.favorite_books}")
                print(f"Любимые жанры: {data_block.favorite_genre}")
                print(f"Игнорируемые книги: {data_block.ignored_books}")
            else:
                print("Записей нет, добавьте книги")
                
    def generate_report_return(self, user_id):
        '''печать отчета по пользователю Return'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                data = f"\nПользователь id: {data_block.user_id}\n\n\U0001F4D6--Любимые книги:\n{split_words_with_index(data_block.favorite_books)}\n\n\U00002764--Любимые жанры:\n{split_words_with_index(data_block.favorite_genre)}\n\n\U00002705--Игнорируемые книги:\n{split_words_with_index(data_block.ignored_books)}"
                return data


    def generate_report_books(self, user_id):
        '''печать отчета по любимым книгам'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                split_words_with_index(data_block.favorite_books)
            else:
                print("Записей нет, добавьте книги")
                

    def generate_report_ganre(self, user_id):
        '''печать отчета по любимым книгам'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                split_words_with_index(data_block.favorite_genre)
            else:
                print("Записей нет, добавьте книги")
                
    def generate_report_ignore(self, user_id):
        '''печать отчета по любимым книгам'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                split_words_with_index(data_block.ignored_books)
            else:
                print("Записей нет, добавьте книги")                                

    def generate_str_books(self, user_id):
        '''печать строки по любимым книгам'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                my_string = ', '.join(data_block.favorite_books)
                return my_string

    def generate_str_genre(self, user_id):
        '''печать строки по любимым жанрам'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                my_string = ', '.join(data_block.favorite_genre)
                return my_string
    
    def generate_str_ignored(self, user_id):
        '''печать строки по игнорируемым'''
        self.load_from_json()
        for data_block in self.data:
            if data_block.user_id == user_id:        
                my_string = ', '.join(data_block.ignored_books)
                return my_string

    def add_data(self, user):
        '''добавить запись пользователя'''
        self.load_from_json()
        user.favorite_books = [user.favorite_books] if isinstance(user.favorite_books, str) else user.favorite_books
        user.favorite_genre = [user.favorite_genre] if isinstance(user.favorite_genre, str) else user.favorite_genre
        user.ignored_books = [user.ignored_books] if isinstance(user.ignored_books, str) else user.ignored_books       
        user_exists = False             # флаг что пользователь не найден
        for data_block in self.data:
            if data_block.user_id == user.user_id:
                # проверка на дубликаты любимых книг
                for user_book in user.favorite_books:
                    if user_book != "":                    
                        if user_book not in data_block.favorite_books:
                            data_block.favorite_books.append(user_book)
                # проверка на дубликаты категорий
                for user_ganre in user.favorite_genre:
                    if user_ganre != "":
                        if user_ganre not in data_block.favorite_genre:
                            data_block.favorite_genre.extend(user.favorite_genre)
                # проверка на дубликаты игнорируемых книг
                for user_ignore in user.ignored_books:
                    if user_ignore != "":
                        if user_ignore not in data_block.ignored_books:
                            data_block.ignored_books.extend(user.ignored_books)
                self.save_to_json()
                user_exists = True
                break   
        if not user_exists:
            self.data.append(user)
            self.save_to_json()
            print(f"Создана запись для пользователя id:{user.user_id}")
            Logger.info(f"Создана запись для пользователя id:{user.user_id}")
        else:
            print(f"Добавлена запись для пользователя {user.user_id}")
            Logger.info(f"Добавлена запись для пользователя id:{user.user_id}")
            
    def clear_book(self, user_id, i_category, i_item):
        '''удаление записи'''
        i_item = i_item -1
        self.load_from_json()
        try:
            for data_block in self.data:
                if data_block.user_id == user_id:
                    if i_category == 1:
                        data_block.favorite_books.pop(i_item)
                        self.save_to_json()
                    elif i_category == 2:
                        data_block.favorite_genre.pop(i_item)
                        self.save_to_json()
                    elif i_category == 3:
                        data_block.ignored_books.pop(i_item)
                        self.save_to_json()                    
                    else:
                        print("Неверный диапазон!\n Введите значение от 1 до 3, где: \n 1- Удаление любимой книги\n 2- Удаление любимого жанра\n 3- Удаление игнорируемой книги")
        except:
            print("Введите категории номерами")
            Logger.exception('Произошла ошибка', sep=' | ')

db1 = Database()
users = []
Logger.info('Программа была запущена', is_traceback=True)


@bot.message_handler(commands=['start', 'help'])
def menu(message): 
    chat_id = message.chat.id  # Получаем ID чата
    user_id_number = message.from_user.id  # Получаем ID пользователя
#  клавитатура
    keyboardmain = types.InlineKeyboardMarkup(row_width=1)  
    but_1 = types.InlineKeyboardButton(text ='\U0001F3AC  Добавление интересов', callback_data='call_1')
    but_2 = types.InlineKeyboardButton(text ='\U0000270F  Редактирование интересов', callback_data='call_2')
    but_3 = types.InlineKeyboardButton(text ='\U0001F50D  Отчет по интересам', callback_data='call_3')
    but_4 = types.InlineKeyboardButton(text ='\U0001F37F  ПОДГОТОВИТЬ ВЫБОРКУ! \U0001F680', callback_data='call_4')
    but_about = types.InlineKeyboardButton(text ='\u2139  О чат боте', callback_data='call_about')
    keyboardmain.add(but_1, but_2, but_3, but_4, but_about)
 # приветственное сообщение
    bot.send_message(message.chat.id,'Добро пожаловать! \U0001F916 \nЯ - <b>{1.first_name}</b>, работаю на искусственном интеллекте и готовлю вам интеллектуаьные подборки фильмов и сериалов, исходя из ваших предпочтений \U0001F3A6 \n\nУкажите свои любимые фильмы и сериалы в формате\n Фильм - Название, например:\n"Фильм - Джентельмены удачи" или \n"Сериал - Друзья".\nЧем больше интересов Вы укажете, тем точнее будет выборка!'.format(message.from_user, bot.get_me()), parse_mode='html',reply_markup=keyboardmain)

 # отсылка в меню
def menu_short(call): 
    #keyboard
    keyboardmain_short = types.InlineKeyboardMarkup(row_width=1)  
    but_menu_short = types.InlineKeyboardButton(text =' В меню', callback_data='menu')
    keyboardmain_short.add(but_menu_short)
    # message
    bot.send_message(message.chat.id,'Войдите в меню'.format(message.from_user, bot.get_me()), parse_mode='html',reply_markup=keyboardmain_short)

#---вешаем обработчик событий на нажатие всех inline-кнопок
@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):
    #о боте
    if call.data == 'call_about':
        keyboard_about = types.InlineKeyboardMarkup(row_width=1)
        but_menu = types.InlineKeyboardButton(text ='В меню', callback_data='menu')
        keyboard_about.add(but_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = "Привет!\nБот создан для создания подборок фильмов \U0001F3AC, основанных на анализе ваших персональных предпочтениях и интересах в кино \U0001F50D\n\nРаботает с применением библиотеки искусственного интеллекта OpenAI \U0001F916\n\nНаслаждайтесь просмотром с удовольствием! \U0001F37F\n\nАвтор Чуян А.А.",reply_markup=keyboard_about)
    elif call.data == 'menu':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=menu(call.message))
    
#---подменю    
    elif call.data == 'call_1':
        keyboardmain = types.InlineKeyboardMarkup(row_width=1)  
        but_1_1 = types.InlineKeyboardButton(text ='\U0001F4D6 Добавление любимого фильма или сериала', callback_data='call_1_1')
        but_1_2 = types.InlineKeyboardButton(text ='\U00002764 Добавление любимого жанра', callback_data='call_1_2')
        but_1_3 = types.InlineKeyboardButton(text ='\U00002705 Добавление игнорируемоего фильма', callback_data='call_1_3')
        but_menu = types.InlineKeyboardButton(text ='Переход в меню', callback_data='menu')
        keyboardmain.add(but_1_1, but_1_2, but_1_3, but_menu)
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='<b>-------------Выберите раздел:--------------</b>', reply_markup=keyboardmain, parse_mode='HTML')
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboardmain)
       
    elif call.data == 'call_1_1':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите имя любимого фильма: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_1_1) #добавление любимой книги
    
    elif call.data == 'call_1_2':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите имя любимого жанра: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_1_2) #добавление любимого жанра
        
    elif call.data == 'call_1_3':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите фильмы, которые не нужно показывать: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_1_3) #добавление игнор книг
# \U0001F4D6--Любимые книги:\U00002764--Любимые жанры:\n\U00002705--Игнорируемые книги    
    elif call.data == 'call_2':
        keyboardmain = types.InlineKeyboardMarkup(row_width=1)  
        but_2_1 = types.InlineKeyboardButton(text ='\U0001F4D6\U0001f5d1 Удаление фильма из списка любимых', callback_data='call_2_1')
        but_2_2 = types.InlineKeyboardButton(text ='\U00002764\U0001f5d1 Удаление жанра из списка любимых', callback_data='call_2_2')
        but_2_3 = types.InlineKeyboardButton(text ='\U00002705\U0001f5d1 Удаление фильма из списка игнорируемых', callback_data='call_2_3')
        but_menu = types.InlineKeyboardButton(text ='Переход в меню', callback_data='menu')
        keyboardmain.add(but_2_1, but_2_2, but_2_3, but_menu)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='<b>----Выберите раздел:</b>', reply_markup=keyboardmain, parse_mode='HTML')
               
    elif call.data == 'call_2_1':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите номер фильма для удаления: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_2_1)  

    elif call.data == 'call_2_2':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите номер жанра для удаления: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_2_2) 
        
    elif call.data == 'call_2_3':
        msg = bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = '\n Введите номер игнорируемой книги для удаления: (0 - Переход в меню)')
        bot.register_next_step_handler(msg, f_menu_2_3) 

    elif call.data == 'call_3':
        keyboard_about = types.InlineKeyboardMarkup(row_width=1)
        but_menu = types.InlineKeyboardButton(text ='В меню', callback_data='menu')
        keyboard_about.add(but_menu)
        user_id_number = call.from_user.id
        user = User(user_id_number, "", "", "")
        report_books = db1.generate_report_return(user_id_number)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"Список ваших интересов:\n {report_books}",reply_markup=keyboard_about)

    elif call.data == 'call_4':
        try:
            keyboard_about = types.InlineKeyboardMarkup(row_width=1)
            but_menu = types.InlineKeyboardButton(text ='В меню', callback_data='menu')
            keyboard_about.add(but_menu)
            user_id_number = call.from_user.id
            user = User(user_id_number, "", "", "")
            question = f"Подбери мне фильмы и сериалы, которые бы мне понравились, учитывая, что мои любимые фильмы и сериалы, которые я уже посмотрел: {db1.generate_str_books(user_id_number)} \nУчти, что мои любимые жанры: {db1.generate_str_genre(user_id_number)} \nНе предлагай мне фильмы и сериалы из списка: {db1.generate_str_ignored(user_id_number)} \nВыдай результат по паре фильмов и одному сериалу на каждый жанр из перечисленных мною в формате:\nЖанр:\nФильм, Автор, год издания\nФильм, Автор, год издания\nСериал, Автор, год издания\n\n"
            # print(question)
            recomend_books = question_ai(question)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"\U0001F916 Ваша интеллектуальная подборка:\n {recomend_books}",reply_markup=keyboard_about)
            Logger.info(f"Обработан запрос пользователя id:{user.user_id} ")
        except Exception as e:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = f"Нейросеть временно недоступна, попросите раработчика заплатить за подписку или поддержите его в этом -)",reply_markup=keyboard_about)
            Logger.exception('Произошла ошибка', sep=' | ')

#//обработчики результатов ввода
#добавление любимой книги
def f_menu_3(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = message.text          #полученный текст
        if date == "0":
            menu(message)
        else:
            user = User(user_id_number, date, "", "")
            db1.add_data(user)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)
#добавление любимого жанра
def f_menu_1_1(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = message.text          #полученный текст
        if date == "0":
            menu(message)
        else:
            user = User(user_id_number, date, "", "")
            db1.add_data(user)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)
#добавление любимого жанра
def f_menu_1_2(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = message.text          #полученный текст
        if date == "0":
            menu(message)
        else:
            user = User(user_id_number, "", date, "")
            db1.add_data(user)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)
#добавление игнорируемых книг
def f_menu_1_3(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = message.text          #полученный текст
        if date == "0":
            menu(message)
        else:
            user = User(user_id_number, "", "", date)
            db1.add_data(user)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)

#удаление любимой книги
def f_menu_2_1(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = int(message.text)          #полученный текст
        if date == 0:
            menu(message)
        else:
            user = User(user_id_number, "", "", "")
            db1.clear_book(user_id_number, 1, date)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)
#удаление любимого жанра
def f_menu_2_2(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = int(message.text)          #полученный текст
        if date == 0:
            menu(message)
        else:
            user = User(user_id_number, "", "", "")
            db1.clear_book(user_id_number, 2, date)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)
#удаление любимого жанра
def f_menu_2_3(message):
    try:
        chat_id = message.chat.id
        user_id_number = message.from_user.id
        date = int(message.text)          #полученный текст
        if date == 0:
            menu(message)
        else:
            user = User(user_id_number, "", "", "")
            db1.clear_book(user_id_number, 3, date)
            users.append(user)
            #отчет
            report_books = db1.generate_report_return(user_id_number)
            bot.send_message(chat_id=message.chat.id, text = f"Список ваших интересов:\n {report_books}")    #информационное сообщение
            menu(message)
    except Exception as e:
        bot.reply_to(message, 'Неверный диапазон!')
        Logger.exception('Произошла ошибка', sep=' | ')
        menu(message)        
        

if __name__ == "__main__":
    bot.polling()


# while True:
#     try:
#         m0 = int(input("\n--Генератор интересного чтива-- Автор Чуян А.А. \n--Выберите задачу: \n 1- Добавление интересов\n 2- Удаление интересов\n 3- Отчет по интересам\n 4- Подготовить подборку книг по интересам\n   0 - Выход\n    : "))
#         # подменю добавления
#         if m0 == 1:     
#             m1 = int(input("\n----Выберите задачу: \n 1- Добавление любимой книги\n 2- Добавление любимого жанра\n 3- Добавление игнорируемой книги\n 0 - Переход в меню\n  : "))
#             if m1 == 1:
#                 print("Список ваших любимых книг: ")
#                 db1.generate_report_books(user_id_number)
#                 m1_m1 = input('Введите название любимой книги: ')
#                 user = User(user_id_number, m1_m1, "", "")
#                 db1.add_data(user)
#                 users.append(user)
#                 print("Добавлено")
#                 print("Список ваших любимых книг: ")
#                 db1.generate_report_books(user_id_number)
#                 pass
#             elif m1 == 2:
#                 print("Список ваших любимых жанров: ")
#                 db1.generate_report_ganre(user_id_number)
#                 m1_m2 = input('Введите название любимого жанра: ')
#                 user = User(user_id_number, "", m1_m2, "")
#                 db1.add_data(user)
#                 users.append(user)
#                 print("Добавлено")
#                 print("Список ваших любимых жанров: ")
#                 db1.generate_report_ganre(user_id_number)
#                 pass
#             elif m1 == 3:
#                 print("Список ваших игнорируемых книг: ")
#                 db1.generate_report_ignore(user_id_number)
#                 m1_m3 = input('Введите название игнорируемых книг: ')
#                 user = User(user_id_number, "", "", m1_m3)
#                 db1.add_data(user)
#                 users.append(user)
#                 print("Добавлено")
#                 print("Список ваших игнорируемых книг: ")
#                 db1.generate_report_ignore(user_id_number)
#                 pass
#             elif m1 == 0:
#                 print("Выход в меню")
#                 break
#             else:
#                 print("Неправильный ввод. Пожалуйста, выберите существующую задачу.")
#                 Logger.error('Неверный ввод!', is_traceback=True)
#         # подменю удаления
#         elif m0 == 2:     
#             m2 = int(input("\n----Выберите задачу: \n 1- Удаление любимой книги\n 2- Удаление любимого жанра\n 3- Удаление игнорируемой книги\n 0 - Переход в меню\n  : "))
#             if m2 in [0, 1, 2 ,3]:
#                 if m2 == 1:
#                     print("Список ваших любимых книг: ")
#                     db1.generate_report_books(user_id_number)
#                     m2_m1 = int(input("\nВыберите номер книги для удаления (0 - для выхода): \n  : "))
#                     if m2_m1 != 0:
#                         db1.clear_book(user_id_number, 1, m2_m1)
#                         print("Удалено")
#                         print("Список ваших любимых книг: ")
#                         db1.generate_report_books(user_id_number)
#                         pass   
#                     else:
#                         print("[ВНИМАНИЕ]-Неверный диапазон")
#                         pass
#                 elif m2 == 2:
#                     print("Список ваших любимых жанров: ")
#                     db1.generate_report_ganre(user_id_number)
#                     m2_m2 = int(input("\nВыберите жанр для удаления: \n  : "))
#                     if m2_m2 != 0:
#                         db1.clear_book(user_id_number, 2, m2_m2)
#                         print("Удалено")
#                         print("Список ваших любимых жанров: ")
#                         db1.generate_report_ganre(user_id_number)
#                         pass
#                     else:
#                         print("[ВНИМАНИЕ]-Неверный диапазон")
#                         pass                    
#                 elif m2 == 3:
#                     print("Список ваших игнорируемых книг: ")
#                     db1.generate_report_ignore(user_id_number)
#                     m2_m3 = int(input("\nВыберите игнорируемую книгу для удаления: \n  : "))
#                     if m2_m3 != 0:    
#                         db1.clear_book(user_id_number, 3, m2_m2)
#                         print("Удалено")
#                         print("Список ваших игнорируемых книг: ")
#                         db1.generate_report_ignore(user_id_number)
#                         pass
#                     else:
#                         print("[ВНИМАНИЕ]-Неверный диапазон")
#                         pass
#                 elif m2 == 0:
#                     print("Выход в меню")
#                     break
#             else:
#                 print("Неправильный ввод. Пожалуйста, выберите существующую задачу.")
#         # подменю отчета
#         elif m0 == 3: 
#             print("----Генерация полного отчета----")
#             print("----Список ваших любимых книг: ")
#             db1.generate_report_books(user_id_number)
#             print("----Список ваших любимых жанров: ")
#             db1.generate_report_ganre(user_id_number)
#             print("----Список ваших игнорируемых книг: ")
#             db1.generate_report_ignore(user_id_number)            
#             continue
#         # подменю бота
#         elif m0 == 4: 
#             question = f"Подбери мне книги, которые бы мне понравились, учитывая мои любимые книги, которые я уже прочитал: {db1.generate_str_books(user_id_number)} \nУчти, что мои любимые жанры: {db1.generate_str_genre(user_id_number)} \nНе предлагай мне книги: {db1.generate_str_ignored(user_id_number)} \nВыдай результат по паре книг на каждый жанр в формате: Жанр: Книга, Автор"
#             # print(question)
#             print(question_ai(question))

#         elif m0 == 0:
#             print("Программа завершена.")
#             Logger.info('Программа была завершена', is_traceback=True)
#             break
#     except:
#         print("Ошибка")
#         Logger.exception('Произошла ошибка', sep=' | ')

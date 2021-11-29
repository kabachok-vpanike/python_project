"""
База данных: prprpr.db
поля:
    TAGS: теги, которые выбрал пользователь при регистрации (разделитель #)
    CHAT_ID: уникальный id пользователя, выдаваемый телеграмом
    USER_BIO: описание, указанное пользователем
    MATCHING: теги пользователей, которые подходят этому человеку (разделитель #)
    USER_HEARTS: теги пользователей, которым понравился этот человек (разделитель #)
    USER_NAME: имя, указанное пользователем
    CONFIRMED_MATCH: теги пользователей, которые выбрал этот человек, смотря анкеты (разделитель #)
    LAST_COFFEE_DATE: последняя дата, от которой был назначен случайный кофе
    THIS_WEEK_ID: id пользователя, с которым на этой неделе должен встретиться этот человек
"""

"""
TODO:
    алгоритм мэтчинга пользователей по тегам
    обработка кнопки agreement
"""

import sqlite3

import telebot
from telebot import types
from random import randint
from datetime import datetime

token = '2119785947:AAGrAj1dQgJh2VOC8WN4yHGLK5mk_L_mLJ4'
bot = telebot.TeleBot(token)

global global_markup
global keyboard_now
global message_with_button_id
global user_id_now
global ind_of_match
global id_of_inline_keyboard
global array_of_matching
global array_of_invites

ind_of_match = 0


@bot.message_handler(commands=['start'])
def start_message(message):
    global global_markup
    bot.send_message(message.chat.id, 'Привет, это coffinder!')
    global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Зарегистрироваться")
    global_markup.add(item1)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=global_markup)


@bot.message_handler(commands=['text'])
def user_message(message):
    pass


tag_buttons = ["Фильмы, Сериалы", "Спорт", "Здоровье и диета", "Путешествия", "Животные", "Музыка", "Видеоигры"]
emoji_buttons = ["🎥 Фильмы, Сериалы", "🏃 Спорт", "🍰 Здоровье и диета", "✈ Путешествия", "🐱 Животные", "🎶 Музыка",
                 "💻 Видеоигры"]


def is_register(user_id):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute('''SELECT * FROM USER_DATA''')
    t = False
    for column in data:
        if column[1] == str(user_id):
            t = True
    return t


def give_random_user(message):
    global array_of_matching
    array_of_matching = define_array_of_matching(message)
    return array_of_matching[randint(0, len(array_of_matching) - 1)]


def give_user_bio(chat_id):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(chat_id)).fetchone()
    sqlite_connection.close()
    return data[2]


def give_user_name(chat_id):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(chat_id)).fetchone()
    sqlite_connection.close()
    return data[5]


def is_this_confirmed_match(user_id_1, user_id_2):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(user_id_1)).fetchone()
    return user_id_2 in data[6]


def assign_coffee_data(id_of_user):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    cur_date = datetime.now()
    current_ddmm = str(cur_date.day) + '.' + str(cur_date.month)
    cursor.execute(
        """UPDATE USER_DATA SET LAST_COFFEE_DATE = '{}' WHERE CHAT_ID = '{}'""".format(current_ddmm, id_of_user))
    sqlite_connection.commit()


def assign_coffee_id(id_of_user, id_of_coffee):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    cursor.execute(
        """UPDATE USER_DATA SET THIS_WEEK_ID = '{}' WHERE CHAT_ID = '{}'""".format(id_of_coffee, id_of_user))
    sqlite_connection.commit()


def check_if_week_passed(id_of_user):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(id_of_user)).fetchone()
    if data[7] is None:
        return True
    cur_date = datetime.now()
    date1 = datetime.strptime(str(cur_date.day) + '.' + str(cur_date.month), "%d.%m")
    date2 = datetime.strptime(data[7], "%d.%m")
    return abs((date1 - date2).days) >= 7


def give_coffee_id(id_of_user):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(id_of_user)).fetchone()
    return data[8]


def register(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute('''SELECT * FROM USER_DATA''')
    t = True
    for column in data:
        if column[1] == str(message.chat.id):
            t = False
    if t:
        sqlite_insert_query = """INSERT INTO USER_DATA
                                          (CHAT_ID, TAGS)
                                         VALUES
                                          ('{}', '{}');""".format(str(message.chat.id), '')

        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
        return True
    else:
        cursor.close()
        return False


@bot.message_handler(content_types='text')
def message_reply(message):
    global tag_buttons
    global global_markup
    global keyboard_now
    global id_of_inline_keyboard
    global ids_of_hearts
    if message.text == "Найти случайный кофе":
        if check_if_week_passed(message.chat.id):
            bot.send_message(chat_id=message.chat.id, text="Ваш случайный кофе на эту неделю:")
            id_of_random_user = give_random_user(message)

            bot.send_message(chat_id=message.chat.id,
                             text=str(give_user_name(id_of_random_user)) + "\n" + str(give_user_bio(id_of_random_user)))
            assign_coffee_data(message.chat.id)
            assign_coffee_id(message.chat.id, id_of_random_user)
        else:
            bot.send_message(chat_id=message.chat.id, text="У вас уже есть кофе на эту неделю:")
            id_of_coffee = give_coffee_id(message.chat.id)
            bot.send_message(chat_id=message.chat.id,
                             text=give_user_name(id_of_coffee) + "\n" + give_user_bio(id_of_coffee))
    if message.text == "Посмотреть мои мэтчи":
        global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Перейти к просмотру анкет")
        item2 = types.KeyboardButton("Найти случайный кофе")
        global_markup.add(item1)
        global_markup.add(item2)
        id_of_inline_keyboard = message.message_id + 2
        bot.send_message(chat_id=message.chat.id, text='Загружаем ваши мэтчи..', reply_markup=global_markup)
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id)).fetchone()
        if data[4] is None:
            bot.send_message(message.chat.id, "Нет мэтчей")
        else:

            ids_of_hearts = data[4][1:].split('#')
            if len(ids_of_hearts) > 0 and ids_of_hearts[0] == '':
                bot.send_message(message.chat.id, "Нет мэтчей")
            else:
                ind_of_heart = 0
                keyboard_now = telebot.types.InlineKeyboardMarkup(row_width=1)
                global array_of_invites
                # print(ids_of_hearts)
                for i in ids_of_hearts:
                    keyboard_now.add(
                        telebot.types.InlineKeyboardButton(str(give_user_name(i)), callback_data='heart_' + str(i)))
                    ind_of_heart += 1
                bot.send_message(chat_id=message.chat.id, text='Вас приглашают на кофе:', reply_markup=keyboard_now)

    if message.text == "Перейти к просмотру анкет":
        if not (is_register(message.chat.id)):
            bot.send_message(message.chat.id, 'Зарегистрируйтесь, чтобы смотреть анкеты!')
        else:
            sqlite_connection = sqlite3.connect('prprpr.db')
            cursor = sqlite_connection.cursor()
            data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id)).fetchone()
            data = list(data)
            data = data[3][1:].split('#')
            keyboard_now = telebot.types.InlineKeyboardMarkup(row_width=3)
            keyboard_now.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                             telebot.types.InlineKeyboardButton('☕️', callback_data='send_match'),
                             telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
            global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Посмотреть мои мэтчи")
            item2 = types.KeyboardButton("Найти случайный кофе")
            global_markup.add(item1)
            global_markup.add(item2)
            bot.send_message(chat_id=message.chat.id, text='Загружаем анкеты..', reply_markup=global_markup)

            can_edit = False
            global user_id_now
            global ind_of_match
            global array_of_matching
            array_of_matching = data
            user_id_now = data[0]  # data[0]
            ind_of_match = 0
            id_of_inline_keyboard = message.message_id + 2
            bot.send_message(message.chat.id, give_user_name(data[0]) + '\n' + give_user_bio(data[0]),
                             reply_markup=keyboard_now)  # data[0]

    if message.text == "Зарегистрироваться":
        if register(message):
            keyboard_now = telebot.types.InlineKeyboardMarkup()
            for butt in tag_buttons:
                keyboard_now.add(telebot.types.InlineKeyboardButton(text=butt, callback_data=butt))

            global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Выбрал!")
            global_markup.add(item1)

            bot.send_message(message.chat.id, 'Вы зарегистрировались!', reply_markup=global_markup)

            bot.send_message(message.chat.id, text="Выберите наиболее интересные для вас темы:",
                             reply_markup=keyboard_now)
        else:
            bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')

    if message.text == "Выбрал!":
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(str(message.chat.id)))
        person = t.fetchone()
        q = cursor.execute("""SELECT * FROM USER_DATA""")
        matching = ""
        for i in q:
            if i[1] != person[1]:
                matching += '#' + str(i[1])
        cursor.execute(
            """UPDATE USER_DATA SET MATCHING = '{}' WHERE CHAT_ID = '{}'""".format(matching, str(person[1])))
        sqlite_connection.commit()
        cursor.close()

        markup = telebot.types.InlineKeyboardMarkup()
        rem = types.ReplyKeyboardMarkup(resize_keyboard=True)
        fake_b = types.KeyboardButton("")
        rem.add(fake_b)
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1, reply_markup='')
        global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Выход")
        global_markup.add(item1)
        bot.send_message(chat_id=message.chat.id, text='Замечательно!', reply_markup=global_markup)
        markup = telebot.types.InlineKeyboardMarkup()
        sent = bot.send_message(chat_id=message.chat.id, text='Как к вам будут обращаться другие пользователи?',
                                reply_markup='')
        bot.register_next_step_handler(sent, user_name)


def user_name(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id))
    t = t.fetchone()
    cursor.execute(
        """UPDATE USER_DATA SET USER_NAME = '{}' WHERE CHAT_ID = '{}'""".format(message.text, t[1]))
    sqlite_connection.commit()
    sent = bot.send_message(chat_id=message.chat.id, text='Напишите, немного о себе:',
                            reply_markup='')
    bot.register_next_step_handler(sent, user_bio)


def user_bio(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id))
    for q in t:
        cursor.execute(
            """UPDATE USER_DATA SET USER_BIO = '{}' WHERE CHAT_ID = '{}'""".format(message.text, q[1]))
        sqlite_connection.commit()

    global global_markup
    global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Перейти к просмотру анкет")
    item2 = types.KeyboardButton("Найти случайный кофе")
    global_markup.add(item1)
    global_markup.add(item2)
    bot.send_message(chat_id=message.chat.id, text='Превосходно! Вам доступен просмотр анкет',
                     reply_markup=global_markup)


def define_array_of_matching(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id))
    per = t.fetchone()
    return per[3][1:].split('#')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global ind_of_match
    global array_of_matching
    global id_of_inline_keyboard
    global keyboard_now
    # global ids_of_hearts
    if 'agreement' in call.data:
        bot.answer_callback_query(callback_query_id=call.id, text="Ура! Вам доступен хендл пользователя для связи",
                                  show_alert=False)
    if 'dismatch' in call.data:
        bot.answer_callback_query(callback_query_id=call.id, text="Ничего страшного, можете поискать ещё",
                                  show_alert=False)
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        data = cursor.execute(
            """SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(call.message.chat.id)).fetchone()
        edited_hearts = data[4].replace('#' + call.data[8:], "")
        data = cursor.execute("""UPDATE USER_DATA SET USER_HEARTS = '{}' WHERE CHAT_ID = '{}'""".format(
            edited_hearts, call.message.chat.id))
        sqlite_connection.commit()
    if call.data == 'back_to_matches':

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Вас приглашают на кофе:")
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        data = cursor.execute(
            """SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(call.message.chat.id)).fetchone()

        keyboard_now = telebot.types.InlineKeyboardMarkup(row_width=2)
        ids_of_hearts = data[4][1:].split('#')
        if len(ids_of_hearts) > 0 and ids_of_hearts[0] == '':
            bot.send_message(chat_id=call.message.chat.id, text="Нет новых мэтчей")
        else:
            for i in ids_of_hearts:
                keyboard_now.add(
                    telebot.types.InlineKeyboardButton(str(give_user_name(i)), callback_data='heart_' + str(i)))
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          reply_markup=keyboard_now)
    if 'heart_' in call.data:
        keyb = telebot.types.InlineKeyboardMarkup()
        keyb.row(telebot.types.InlineKeyboardButton("👍", callback_data='agreement' + str(call.data[6:])),
                 telebot.types.InlineKeyboardButton("👎", callback_data='dismatch' + str(call.data[6:])))
        keyb.add(telebot.types.InlineKeyboardButton("⬅", callback_data='back_to_matches'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=give_user_name(call.data[6:]) + '\n' + give_user_bio(call.data[6:]))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyb)
        id_of_inline_keyboard = call.message.message_id

    if call.data == 'send_match':
        array_of_matching = define_array_of_matching(call.message)
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(array_of_matching[ind_of_match]))
        person = t.fetchone()
        if person[4] is None:
            cursor.execute(
                """UPDATE USER_DATA SET USER_HEARTS = '{}' WHERE CHAT_ID = '{}'""".format(
                    '#' + str(call.message.chat.id), array_of_matching[ind_of_match]))
        else:
            cursor.execute(
                """UPDATE USER_DATA SET USER_HEARTS = '{}' WHERE CHAT_ID = '{}'""".format(
                    str(person[4]) + '#' + str(call.message.chat.id), array_of_matching[ind_of_match]))
        keyb = telebot.types.InlineKeyboardMarkup(row_width=3)
        keyb.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                 telebot.types.InlineKeyboardButton('❌', callback_data='cancel'),
                 telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=keyb)
        t = cursor.execute(
            """SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(array_of_matching[ind_of_match])).fetchone()
        if t[6] is None:
            conf_match = '#' + str(call.message.chat.id)
        else:
            conf_match = t[6] + '#' + str(call.message.chat.id)
        cursor.execute(
            """UPDATE USER_DATA SET CONFIRMED_MATCH = '{}' WHERE CHAT_ID = '{}'""".format(
                conf_match, array_of_matching[ind_of_match]))
        sqlite_connection.commit()
        t = cursor.execute(
            """SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(call.message.chat.id)).fetchone()
        if t[6] is None:
            conf_match = '#' + str(array_of_matching[ind_of_match])
        else:
            conf_match = t[6] + '#' + str(array_of_matching[ind_of_match])
        cursor.execute(
            """UPDATE USER_DATA SET CONFIRMED_MATCH = '{}' WHERE CHAT_ID = '{}'""".format(
                conf_match, call.message.chat.id))
        sqlite_connection.commit()
    if call.data == 'cancel':
        keyb = telebot.types.InlineKeyboardMarkup(row_width=3)
        keyb.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                 telebot.types.InlineKeyboardButton('☕', callback_data='send_match'),
                 telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.chat.id,
                                      reply_markup=keyb)
    if call.data == 'next' or call.data == 'prev':
        array_of_matching = define_array_of_matching(call.message)
        if call.data == 'next':
            ind_of_match = (ind_of_match + 1) % len(array_of_matching)
        if call.data == 'prev':
            ind_of_match = (ind_of_match - 1) % len(array_of_matching)
        keyb = telebot.types.InlineKeyboardMarkup(row_width=3)
        keyb.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                 telebot.types.InlineKeyboardButton('☕', callback_data='send_match'),
                 telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=give_user_name(array_of_matching[ind_of_match]) + '\n' + give_user_bio(
                                  array_of_matching[ind_of_match]),
                              reply_markup=keyb)

    global tag_buttons
    if call.data in tag_buttons:
        sqlite_connection = sqlite3.connect('prprpr.db')
        cursor = sqlite_connection.cursor()
        t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(call.message.chat.id))
        user_tags = ""
        for q in t:
            user_tags = q[0]
            if call.data not in q[0]:
                cursor.execute(
                    """UPDATE USER_DATA SET TAGS = '{}' WHERE CHAT_ID = '{}'""".format(q[0] + '#' + call.data, q[1]))
                sqlite_connection.commit()
        markup = telebot.types.InlineKeyboardMarkup()

        for butt in tag_buttons:
            if butt in user_tags:
                if butt == call.data:
                    markup.add(telebot.types.InlineKeyboardButton(text=butt, callback_data=butt))
                    cursor.execute(
                        """UPDATE USER_DATA SET TAGS = '{}' WHERE CHAT_ID = '{}'""".format(
                            user_tags.replace('#' + butt, ''), call.message.chat.id))
                    sqlite_connection.commit()
                else:
                    markup.add(telebot.types.InlineKeyboardButton(text=butt + "✅", callback_data=butt))
            else:
                if butt == call.data:
                    markup.add(telebot.types.InlineKeyboardButton(text=butt + "✅", callback_data=butt))
                else:
                    markup.add(telebot.types.InlineKeyboardButton(text=butt, callback_data=butt))

        cursor.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Выберите наиболее интересные для вас темы:", reply_markup=markup)


bot.polling(True)

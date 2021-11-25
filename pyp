import sqlite3
from contextlib import suppress

import telebot
import telegram as telegram
from telebot import types

token = '2119785947:AAGrAj1dQgJh2VOC8WN4yHGLK5mk_L_mLJ4'
bot = telebot.TeleBot(token)

global global_markup
global keyboard_now
global message_with_button_id
global user_id_now
global ind_of_match
global id_of_inline_keyboard
global array_of_matching


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
        # print(column[1])
        if column[1] == str(user_id):
            t = True
    return t


def give_user_bio(chat_id):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(chat_id)).fetchone()
    sqlite_connection.close()
    return data[2]


def register(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    # sqlite_insert_query = """INSERT INTO USER_DATA
    #                          (CHAT_ID, TAGS)
    #                         VALUES
    #                          ({}, {});""".format(message.chat.id, ' ')
    data = cursor.execute('''SELECT * FROM USER_DATA''')
    t = True
    for column in data:
        # print(column[1])
        if column[1] == str(message.chat.id):
            t = False
    if t:
        sqlite_insert_query = """INSERT INTO USER_DATA
                                          (CHAT_ID, TAGS)
                                         VALUES
                                          ('{}', '{}');""".format(str(message.chat.id), '')

        cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        # bot.send_message(message.chat.id, 'Вы зарегистрировались!')
        cursor.close()
        return True
    else:
        # bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')
        cursor.close()
        return False


@bot.message_handler(content_types='text')
def message_reply(message):
    global tag_buttons
    global global_markup
    global keyboard_now
    if message.text == "Перейти к просмотру анкет":
        if not (is_register(message.chat.id)):
            bot.send_message(message.chat.id, 'Зарегистрируйтесь, чтобы смотреть анкеты!')
        else:
            sqlite_connection = sqlite3.connect('prprpr.db')
            cursor = sqlite_connection.cursor()
            data = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id)).fetchone()
            data = list(data)
            data = data[3][1:].split('#')
            # print(data[3][1:].split('#'))
            keyboard_now = telebot.types.InlineKeyboardMarkup(row_width=3)
            keyboard_now.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                             telebot.types.InlineKeyboardButton('❤️', callback_data='send_match'),
                             telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
            global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Посмотреть мои мэтчи")
            global_markup.add(item1)
            bot.send_message(chat_id=message.chat.id, text='Загружаем анкеты..', reply_markup=global_markup)
            # keyboard_now.add()
            # keyboard_now.add()

            can_edit = False
            # for user in data:
            #   print(user, give_user_bio(user))
            global user_id_now
            global ind_of_match
            global id_of_inline_keyboard
            global array_of_matching
            array_of_matching = data
            user_id_now = data[0]
            ind_of_match = 0
            id_of_inline_keyboard = message.message_id + 2
            bot.send_message(message.chat.id, give_user_bio(data[0]), reply_markup=keyboard_now)
            # for column in data:
            #   if column[1] != str(message.chat.id):
            #  if can_edit:
            #     bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id + 1,
            #                          text=column[2],
            #                         reply_markup=keyboard_now)
            # else:
            #   bot.send_message(message.chat.id, column[2], reply_markup=keyboard_now)
            #  can_edit = True

    if message.text == "Зарегистрироваться":
        if register(message):

            # bot.send_message(message.chat.id, 'Выберите наиболее интересные для вас темы:')
            keyboard_now = telebot.types.InlineKeyboardMarkup()
            for butt in tag_buttons:
                keyboard_now.add(telebot.types.InlineKeyboardButton(text=butt, callback_data=butt))

            # bot.send_message(message.chat.id, 'текст над кнопкой', reply_markup=global_markup)
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

        # global message_with_button_id
        # message_with_button_id = message.message_id
        markup = telebot.types.InlineKeyboardMarkup()
        rem = types.ReplyKeyboardMarkup(resize_keyboard=True)
        fake_b = types.KeyboardButton("")
        rem.add(fake_b)
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1, reply_markup='')
        # global global_markup
        global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton("Выход")
        global_markup.add(item1)
        bot.send_message(chat_id=message.chat.id, text='Замечательно!', reply_markup=global_markup)
        markup = telebot.types.InlineKeyboardMarkup()
        sent = bot.send_message(chat_id=message.chat.id, text='Напишите, немного о себе:',
                                reply_markup='')
        bot.register_next_step_handler(sent, user_bio)
        # global global_markup

        # bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1,
        #                        reply_markup=global_markup)
        # bot.edit_message_text("Ха", message.chat.id, message.message_id)

        # markup.add(telebot.types.InlineKeyboardButton(text="butt" + "✅", callback_data=butt))
        # bot.edit_message_reply_markup(chat_id=message.chat.id, text='Выб')


def user_bio(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id))
    for q in t:
        cursor.execute(
            """UPDATE USER_DATA SET USER_BIO = '{}' WHERE CHAT_ID = '{}'""".format(message.text, q[1]))
        sqlite_connection.commit()

    global global_markup
    # global_markup.add(types.KeyboardButton("Выход"))
    global_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Перейти к просмотру анкет")
    global_markup.add(item1)
    bot.send_message(chat_id=message.chat.id, text='Превосходно!', reply_markup=global_markup)
    # bot.send_message(chat_id=message.chat.id, text='Посм!')


def define_array_of_matching(message):
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(message.chat.id))
    per = t.fetchone()
    return per[3][1:].split('#')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, text='Answer accepted!')
    # answer = 'You made a mistake'
    # if call.data == '4':
    #    answer = 'You answered correctly!'
    global ind_of_match
    global array_of_matching
    global id_of_inline_keyboard
    # ind_of_match = 0
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
                 telebot.types.InlineKeyboardButton('💔', callback_data='cancel'),
                 telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=id_of_inline_keyboard,
                                      reply_markup=keyb)
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=id_of_inline_keyboard,
        #                     text=give_user_bio(array_of_matching[ind_of_match]) + " ",
        #                    reply_markup=keyboard_now)
        # print("Ok")
        #bot.answer_callback_query(call.message.chat.id, "c", show_alert=True)
        # bot.send_message(call.message.chat.id, "123")
        # sqlite_connection.commit()
        # cursor.close()
        # sqlite_connection.close()
    if call.data == 'cancel':
        keyb = telebot.types.InlineKeyboardMarkup(row_width=3)
        keyb.row(telebot.types.InlineKeyboardButton('⬅', callback_data='prev'),
                 telebot.types.InlineKeyboardButton('❤', callback_data='send_match'),
                 telebot.types.InlineKeyboardButton('➡️', callback_data='next'))
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=id_of_inline_keyboard,
                                      reply_markup=keyb)
    if call.data == 'next' or call.data == 'prev':
        array_of_matching = define_array_of_matching(call.message)
        if call.data == 'next':
            ind_of_match = (ind_of_match + 1) % len(array_of_matching)
        if call.data == 'prev':
            ind_of_match = (ind_of_match - 1) % len(array_of_matching)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=id_of_inline_keyboard,
                              text=give_user_bio(array_of_matching[ind_of_match]),
                              reply_markup=keyboard_now)

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
                # user_tags = q[0] + call.data
                # bot.send_message(message.chat.id, 'Выберите наиболее интересные для вас темы:')
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
        # print(q[0], q[1])

        # bot.send_message(call.message.chat.id, answer)
        # call.message.edit_message_text("new text")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Выберите наиболее интересные для вас темы:", reply_markup=markup)


bot.polling(True)

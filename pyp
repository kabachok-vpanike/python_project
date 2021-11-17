import sqlite3

import telebot
from telebot import types

token = '2119785947:AAGrAj1dQgJh2VOC8WN4yHGLK5mk_L_mLJ4'
bot = telebot.TeleBot(token)

global global_markup
global keyboard_now


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
emoji_buttons = ["🎥 Фильмы, Сериалы", "🏃 Спорт", "🍰 Здоровье и диета", "✈ Путешествия", "🐱 Животные", "🎶 Музыка", "💻 Видеоигры"]


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
    if message.text == "Зарегистрироваться":
        if register(message):
            global tag_buttons
            global global_markup
            global keyboard_now
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
        markup = telebot.types.InlineKeyboardMarkup()
        bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id - 1, reply_markup='')
        bot.send_message(chat_id=message.chat.id, text='Замечательно!')
        #markup = telebot.types.InlineKeyboardMarkup()
        #bot.send_message(chat_id=message.chat.id, text='Напишите, немного о себе:')
        
        #markup.add(telebot.types.InlineKeyboardButton(text="butt" + "✅", callback_data=butt))
        #bot.edit_message_reply_markup(chat_id=message.chat.id, text='Выб')


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    # bot.answer_callback_query(callback_query_id=call.id, text='Answer accepted!')
    # answer = 'You made a mistake'
    # if call.data == '4':
    #    answer = 'You answered correctly!'
    sqlite_connection = sqlite3.connect('prprpr.db')
    cursor = sqlite_connection.cursor()
    t = cursor.execute("""SELECT * FROM USER_DATA WHERE CHAT_ID = '{}'""".format(call.message.chat.id))
    user_tags = ""
    global tag_buttons
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

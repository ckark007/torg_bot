from os import name
import telebot
from types import CellType

from telebot.types import Message
import config
from telebot import types
import sqlite3
from random import randint
from time import sleep

from datetime import date, datetime
from threading import Thread
import random
import string
import json
import requests
import time
global client
client = telebot.TeleBot(config.CONFIG['token'])
global api
global token
global phone
token = config.CONFIG['qiwi']
phone = config.CONFIG['phone']

threads=[]

db = sqlite3.connect('users.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id TEXT,
    qrule TEXT,
    cash INTEGER,
    usersinbot INTEGER,
    pay TEXT,
    pay_money INTEGER,
    torg TEXT
    
)""")


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def update():
    pribal = 0
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")

    while True:
        tt = datetime.now()
        
        if tt.hour == 0:
            for x in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{'AdminUsers'}'"):
                pribal = x[0]
            formul = 1 + pribal /100
            cursor.execute('''SELECT * FROM users''')
            records = cursor.fetchall()
            id = ''

            for row in records:
                
                cursor.execute("UPDATE users SET cash = ? WHERE user_id = ?", (row[2] * formul, row[0]))
                db.commit()


        
        sleep(3)




# Перевод на QIWI Кошелек
def send_p2p(api_access_token, to_qw, comment, sum_p2p):
    s = requests.Session()
    s.headers = {'content-type': 'application/json'}
    s.headers['authorization'] = 'Bearer ' + api_access_token
    s.headers['User-Agent'] = 'Android v3.2.0 MKT'
    s.headers['Accept'] = 'application/json'
    postjson = {"id":"","sum":{"amount":"","currency":""},"paymentMethod":{"type":"Account","accountId":"643"}, "comment":"'+comment+'","fields":{"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = sum_p2p
    postjson['sum']['currency'] = '643'
    postjson['fields']['account'] = to_qw
    postjson['comment'] = comment
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments',json = postjson)
    return res.json()


# История платежей - последние и следующие n платежей
def payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()

def send_card(api_access_token, payment_data):
    # payment_data - dictionary with all payment data
    s = requests.Session()
    s.headers['Accept'] = 'application/json'
    s.headers['Content-Type'] = 'application/json'
    s.headers['authorization'] = 'Bearer ' + api_access_token
    postjson = {"id":"","sum": {"amount":"","currency":"643"},"paymentMethod": {"type":"Account","accountId":"643"},"fields": {"account":""}}
    postjson['id'] = str(int(time.time() * 1000))
    postjson['sum']['amount'] = payment_data.get('sum')
    postjson['fields']['account'] = payment_data.get('to_card')
    prv_id = payment_data.get('prv_id')
    if payment_data.get('prv_id') in ['1960', '21012']:
        postjson['fields']['rem_name'] = payment_data.get('rem_name')
        postjson['fields']['rem_name_f'] = payment_data.get('rem_name_f')
        postjson['fields']['reg_name'] = payment_data.get('reg_name')
        postjson['fields']['reg_name_f'] = payment_data.get('reg_name_f')
        postjson['fields']['rec_city'] = payment_data.get('rec_address')
        postjson['fields']['rec_address'] = payment_data.get('rec_address')
        
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/' + prv_id + '/payments', json = postjson)
    return res.json()










def write_users(message):
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")
    db.commit()
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{message.chat.id}'")
    if cursor.fetchone() is None:
        
        users_list = [message.chat.id, 'True', 1, 0, 'nopay', 0, 'False']

        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", users_list)
        db.commit()
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{'AdminUsers'}'")
        if cursor.fetchone() is None:

            #! Поле pay_money админа заноситься процент прибыли
            users_list = ['AdminUsers', 'True', 0, 0, 'admin', 10, 'False']


            cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?);", users_list)
            db.commit()

        for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
            users_in_bot = i[0]
        
            
        cursor.execute(f"UPDATE users SET usersinbot = {1 + int(users_in_bot)} WHERE user_id = '{'AdminUsers'}'")
        db.commit()

        




def pay(message):
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")
    
    
    

    comment = generate_random_string(7)
    
    
    
    
    
    
    
    cursor.execute("UPDATE users SET pay = ? WHERE user_id = ?", (comment, message.chat.id))
    db.commit()
    
    
    
    markup_inline = types.InlineKeyboardMarkup()

    item_pay = types.InlineKeyboardButton(text = 'Оплатить', url='qiwi.com/p/79259058006') #qiwi.com/p/79259058006
    item_check = types.InlineKeyboardButton(text = 'Проверить платёж', callback_data='check')
    item_back = types.InlineKeyboardButton(text = 'Назад', callback_data='bck')
    markup_inline.add(item_pay)
    markup_inline.add(item_check)
    markup_inline.add(item_back)
    client.send_message(message.chat.id, f'Нажмите на кнопку оптатить для перехода к оплате. В комментариях к переводу укажите ключ - {comment}, если вы не укажите его деньги не зачисляться на счёт. После оплаты проверьте её нажав на соответствующую кнопку. Учтите что сумма поступившая на счёт будет с учётом коммиси QIWI. Посмотреть размер коммисии можно при переводе.', reply_markup=markup_inline)
    
        

    

def money_exit(message):
    
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")
    
    
    balance = 0
    
    for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id} '"):
        balance = i[0]
    
    pay = send_p2p(token, message.text,'Вывод денег из торгового бота', float(balance*comiss))
    with open('data.json', 'w', encoding='utf-8') as f:

        json.dump(pay, f, ensure_ascii=False, indent=4)


    client.send_message(message.chat.id, pay['message'])
    
    
    
    

    
    











def reg(message):
    markup_inline = types.InlineKeyboardMarkup()

    item_ok = types.InlineKeyboardButton(text = 'Принять правила', callback_data='ok')
    markup_inline.add(item_ok)
    client.send_message(message.chat.id, 'Правила', reply_markup=markup_inline)






def main(message):
    balance = 0
    users = 0
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")
    
    
    
    
    
    
    try:
        for x in cursor.execute(f"SELECT qrule FROM users WHERE user_id = '{message.chat.id}'"):
            x = x[0].strip()
        if x == 'True':

            for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id}'"):
                balance = i[0]
            
            if balance > 0:
                torg = 'False'
                for i in cursor.execute(f"SELECT torg FROM users WHERE user_id = '{message.chat.id}'"):
                    torg = i[0]
                
                if torg == 'False':

                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item_balance = types.KeyboardButton('💱 Оплатить торгового робота')
                    item_torg = types.KeyboardButton('🟢 Начать торговать')
                    item_exit = types.KeyboardButton('💸 Вывести деньги')
                    item_help = types.KeyboardButton('❓ Тех поддержка')
                else:
                    markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                    item_balance = types.KeyboardButton('💱 Оплатить торгового робота')
                    item_torg = types.KeyboardButton('🔴 Закончить торговать')
                    item_exit = types.KeyboardButton('💸 Вывести деньги')
                    item_help = types.KeyboardButton('❓ Тех поддержка')
                link = '[<Ваш текст>](<https://t.me/joinchat/ZQYVR7Gwl5AxM2Ni>)'
                vip = 'Обсуждения по поводу бота проводяться в чате: https://t.me/joinchat/ZQYVR7Gwl5AxM2Ni'
                markup_reply.add(item_balance, item_exit)
                markup_reply.add(item_torg, item_help)
                
                
                for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
                    users = i[0]
            else:
                markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
                item_balance = types.KeyboardButton('💱 Оплатить торгового робота')
                item_info = types.KeyboardButton('ℹ️ Информация')
                markup_reply.add(item_balance)
                markup_reply.add(item_info)
                for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
                    users = i[0]
            
            
            
            client.send_message(message.chat.id, f'''
💲 Ваш баланс - {balance}
🆔 Ваш ID - {message.chat.id}
🙎‍♂️ Число пользователей - {users}
{vip}''', reply_markup=markup_reply)


        

    
        
    except:
        reg(message)
    
        






            
    ''' except:
        markup_inline = types.InlineKeyboardMarkup()
        item_yes = types.InlineKeyboardButton(text = 'Принять правила', callback_data='ok')
        markup_inline.add(item_yes)
        
        

    

        
        client.send_message(message.chat.id, 'Тут будет сообщение с правилами', reply_markup=markup_inline)'''

        
    

























@client.message_handler(commands=['start'])
def welcom(message):


    
    
    
    
    main(message)
    








@client.message_handler(content_types=['text'])
def get_text(message):

    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
        
    )""")
    markup_inline = types.InlineKeyboardMarkup()
    item_back = types.InlineKeyboardButton(text = 'Назад', callback_data='bck')
    
    markup = types.ReplyKeyboardRemove(selective=False)
    if 'оплатить торгового робота' in message.text.lower():
        markup_inline.add(item_back)
        
        
        
        pay(message)
        
        
    elif 'информация' in message.text.lower():

        markup_inline.add(item_back)

        
        
        
        client.send_message(message.chat.id, 'Информация', reply_markup=markup_inline)
    elif 'тех поддержка' in message.text.lower():
        markup_inline.add(item_back)

        
        
        
        client.send_message(message.chat.id, 'Ссылка на тех поддержку', reply_markup=markup_inline)
    elif 'вывести деньги' in message.text.lower():
        markup_inline.add(item_back)

        
        for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id}'"):
                balance = i[0]

        global comiss
        comiss = 1
        client.send_message(message.chat.id, f'Отправте мне номер телефона QIWI кошелька для вывода денег. Деньги выводятся с коммисией. За раз выводиться вся сумма кошелька с коммисией - {float(balance * comiss)}', reply_markup=markup_inline)
        client.register_next_step_handler(message, money_exit)
    elif 'закончить торговать' in message.text.lower():
        cursor.execute(f"UPDATE users SET torg = ? WHERE user_id = ?", ('False', message.chat.id))
        db.commit()
        client.send_message(message.chat.id, 'Торговля остановлена')
        main(message)
    elif 'начать торговать' in message.text.lower():
        cursor.execute(f"UPDATE users SET torg = ? WHERE user_id = ?", ('True', message.chat.id))
        db.commit()
        client.send_message(message.chat.id, 'Торговля Запущена')
        main(message)

        
        






@client.callback_query_handler(func=lambda call: True)
def answer(call):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qrule TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT
    )""")
    db.commit()
    
        
    if call.data == 'ok':
        client.delete_message(call.message.chat.id, call.message.message_id)
        
        write_users(call.message)
        main(call.message)


    elif call.data == 'bck':
        client.delete_message(call.message.chat.id, call.message.message_id)
        cursor.execute("UPDATE users SET pay = ? WHERE user_id = ?", ('nopay', call.message.chat.id))
        db.commit()
        main(call.message)
    elif call.data == 'check':
        
        comment = ''

        for i in cursor.execute(f"SELECT pay FROM users WHERE user_id = '{call.message.chat.id}'"):
            comment = i[0]
        # последние 20 платежей
        lastPayments = payment_history_last(phone, token, '20','','')
        for payment in lastPayments():
            if payment['comment'] == comment:
                amount = payment['total']['amount']
                break
        for x in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{call.message.chat.id}'"):
            balance = x[0]

            
            cursor.execute("UPDATE users SET cash = ? WHERE user_id = ?", (int(balance) + int(amount), call.message.chat.id))
            db.commit()
            cursor.execute("UPDATE users SET pay = ? WHERE user_id = ?", ('nopay', call.message.chat.id))
            db.commit()
            main(call.message)

        else:
            client.send_message(call.message.chat.id, 'Оплата не найдена. Если вы произвели оплату подождите немножко и ещё раз выполните проверку. Техподдержака - тут ссылка на тех поддержку')

        














thread1=Thread(target=update); threads.append(thread1)
for t in threads:
    t.start()




client.polling(none_stop=True, interval=0)
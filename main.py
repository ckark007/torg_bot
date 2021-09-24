from logging import exception
from os import name
import telebot


from telebot.types import Message
#from types import CellType
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
global comiss
comiss = 1



global minimize_amount
minimize_amount = 7




token = config.CONFIG['qiwi']
phone = config.CONFIG['phone']

threads=[]
global procent_ot_pribali
procent_ot_pribali = 10

#Функция генерации ключей для оплаты

def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))



#функция обновления баланся
def update():
    pribal = 0
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
    )""")

    while True:
        tt = datetime.now()
        
        if tt.hour == 0:
            for x in cursor.execute(f"SELECT pay_money FROM users WHERE user_id = '{'AdminUsers'}'"):
                pribal = x[0]

            formul = 1 + pribal /100
            cursor.execute('''SELECT * FROM users''')
            records = cursor.fetchall()
            id = ''

            for row in records:
                
                cursor.execute("UPDATE users SET cash = ? WHERE user_id = ?", (row[2] * formul, row[0]))
                db.commit()


        
        sleep(40)




# Перевод на QIWI Кошелек
def send_p2p(api_access_token, to_qw, sum_p2p):
    s = requests.Session()
    
    sum_p2p = str(sum_p2p) + '.00'
    s.headers = {'content-type': 'application/json'}
    s.headers['authorization'] = 'Bearer ' + api_access_token
    s.headers['User-Agent'] = 'Android v3.2.0 MKT'
    s.headers['Accept'] = 'application/json'
    
    postjson = {"id":str(int(time.time() * 1000)),"sum":{"amount":str(to_qw),"currency":"643"},"paymentMethod":{"type":"Account","accountId":"643"}, "comment":"Вывод денег","fields":{"account": to_qw}}
    
    
    res = s.post('https://edge.qiwi.com/sinap/api/v2/terms/99/payments', json = postjson)
    return res.json()


# История платежей - последние и следующие n платежей
def payment_history_last(my_login, api_access_token, rows_num, next_TxnId, next_TxnDate):
    s = requests.Session()
    s.headers['authorization'] = 'Bearer ' + api_access_token  
    parameters = {'rows': rows_num, 'nextTxnId': next_TxnId, 'nextTxnDate': next_TxnDate}
    h = s.get('https://edge.qiwi.com/payment-history/v2/persons/' + my_login + '/payments', params = parameters)
    return h.json()



#Запись нового юзера
def write_users(message):
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
    )""")
    db.commit()
    cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{message.chat.id}'")
    if cursor.fetchone() is None:
        
        users_list = [message.chat.id, 'False', 0, 0, 'nopay', 0, 'False', 'True']

        cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?);", users_list)
        db.commit()
        cursor.execute(f"SELECT user_id FROM users WHERE user_id = '{'AdminUsers'}'")
        if cursor.fetchone() is None:

            #! Поле pay_money админа заноситься процент прибыли
            users_list = ['AdminUsers', 'True', 0, 0, 'admin', procent_ot_pribali, 'False', 'True']


            cursor.execute("INSERT INTO users VALUES(?,?,?,?,?,?,?,?);", users_list)
            db.commit()

        for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
            users_in_bot = i[0]
        
            
        cursor.execute(f"UPDATE users SET usersinbot = {1 + int(users_in_bot)} WHERE user_id = '{'AdminUsers'}'")
        db.commit()
    main(message)

        



#функция пополнения баланса
def pay(message):
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
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
    client.send_message(message.chat.id, f'Нажмите на кнопку оплатить для перехода к оплате. В комментариях к переводу укажите ключ - {comment}, если Вы не укажите его, деньги не зачислятся на счёт. После оплаты проверьте её, нажав на соответствующую кнопку. Учтите, что сумма поступившая на счёт будет с учётом комиссии QIWI. Посмотреть размер комиссии можно при переводе. Минимальная сумма пополнения - {str(minimize_amount)}р, если сумма оплаты будет меньше деньги не зачисляться на счёт.', reply_markup=markup_inline)
    
        

    
#aeyrwbz вывода денег
def money_exit(message):
    
    if '+' not in message.text.lower():
        client.send_message(message.chat.id, 'Ваш номер не подходит для перевода')
        main(message)
        return
    
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
    )""")
    
    
    balance = 0
    
    for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id}'"):
        balance = i[0]
        
    exit2 = int(balance * comiss)
    pay = send_p2p(token, str(message.text), str(exit2))
    print(pay)
    
    

    try:
        client.send_message(message.chat.id, pay['message'])
        sleep(1)

    except KeyError:

        cursor.execute("UPDATE users SET cash = ? WHERE user_id = ?", (0, message.chat.id))
        db.commit()
        client.send_message(message.chat.id, 'Оплата прошла успешно')
    main(message)



#Сообщение с правилами
def reg(message):
    markup_inline = types.InlineKeyboardMarkup()

    item_ok = types.InlineKeyboardButton(text = 'Принять правила', callback_data='ok')
    markup_inline.add(item_ok)
    client.send_message(message.chat.id, 'Правила', reply_markup=markup_inline) #!Сдесь надо поменять текст





#Главное меню
def main(message):  # sourcery no-metrics
    balance = 0
    users = 0
    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
    )""")
    
    
    
    
    
    global qrule
    qrule = 'False'
    
    for x in cursor.execute(f"SELECT qrule FROM users WHERE user_id = '{message.chat.id}'"):
        qrule = x[0].strip()
    
    if qrule == 'True':
    

        for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id}'"):
            balance = i[0]
        
        if balance > 0:
            cursor.execute("UPDATE users SET qpay = ? WHERE user_id = ?", ('True', message.chat.id))
            db.commit()
            torg = 'False'
            for i in cursor.execute(f"SELECT torg FROM users WHERE user_id = '{message.chat.id}'"):
                torg = i[0]
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item_balance = types.KeyboardButton('💱 Оплатить торгового робота')
            item_exit = types.KeyboardButton('💸 Вывести деньги')
            item_help = types.KeyboardButton('❓ Тех поддержка')
            if torg == 'False':

                
                
                item_torg = types.KeyboardButton('🟢 Начать торговать')
                
                
            else:
                item_torg = types.KeyboardButton('🔴 Закончить торговать')
            
            vip = 'Обсуждения по поводу бота проводяться в чате: https://t.me/joinchat/ZQYVR7Gwl5AxM2Ni'
            markup_reply.add(item_balance, item_exit)
            markup_reply.add(item_torg, item_help)
            
            
            for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
                users = i[0]
        else:
            vip = ''
            markup_reply = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item_balance = types.KeyboardButton('💱 Оплатить торгового робота')
            item_info = types.KeyboardButton('ℹ️ Информация')
            item_help = types.KeyboardButton('❓ Тех поддержка')
            markup_reply.add(item_balance)
            markup_reply.add(item_info, item_help)
            for i in cursor.execute(f"SELECT usersinbot FROM users WHERE user_id = '{'AdminUsers'}'"):
                users = i[0]
        
        
        
        client.send_message(message.chat.id, f'''
💲 Ваш баланс - {balance}
🆔 Ваш ID - {message.chat.id}
🙎‍♂️ Число пользователей - {users}
{vip}''', reply_markup=markup_reply)


    else:

        reg(message)



@client.message_handler(commands=['start'])
def welcom(message):


    
    main(message)
    



@client.message_handler(content_types=['text'])
def get_text(message):

    db = sqlite3.connect('users.db')
    cursor = db.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id TEXT,
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
        
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

        
        
        
        client.send_message(message.chat.id, 'Тех поддержка: @Nncode', reply_markup=markup_inline)
    elif 'вывести деньги' in message.text.lower():
        markup_inline.add(item_back)

        balance = 0
        for i in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{message.chat.id}'"):
                balance = i[0]

        
        client.send_message(message.chat.id, f'Отправте номер телефона QIWI кошелька для вывода денег. Пример номера телефона - +79021234567, обязательно начинайте со знака +. Деньги выводятся с комиссией. За раз выводится вся сумма кошелька с комиссией -{int(balance * comiss)}', reply_markup=markup_inline)
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
        qpay TEXT,
        cash INTEGER,
        usersinbot INTEGER,
        pay TEXT,
        pay_money INTEGER,
        torg TEXT,
        qrule TEXT
    )""")
    db.commit()
    
        
    if call.data == 'ok':
        client.delete_message(call.message.chat.id, call.message.message_id)
        
        write_users(call.message)
        


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
        last_payments = payment_history_last(phone, token, '10','','')
        
        for payment in last_payments['data']:
            qcomment = payment['comment']
            if comment in qcomment:

                balance = 0
                for x in cursor.execute(f"SELECT cash FROM users WHERE user_id = '{call.message.chat.id}'"):
                    balance = x[0]
                qpay2 = True

                amount = payment['total']['amount']
                if int(amount) >= minimize_amount:

                    cursor.execute("UPDATE users SET pay = ? WHERE user_id = ?", ('nopay', call.message.chat.id))
                    db.commit()
                    #cursor.execute("UPDATE users SET cash = ? WHERE user_id = ?", (int(balance) + int(amount), call.message.chat.id))
                    db.commit()
                    client.send_message(call.message.chat.id, 'Оплата найдена. Деньги занесны на счёт.')
                else:
                    client.send_message(call.message.chat.id, f'Сумма пополнения меньше {minimize_amount} рублей. Деньги не зачислены на счёт')
                
                
                main(call.message)
                break

            else:
                qpay2 = False
        if qpay2 is False:

            client.send_message(call.message.chat.id, 'Оплата не найдена. Если вы произвели оплату подождите немножко и ещё раз выполните проверку. Тех поддержака: @Nncode')


thread1=Thread(target=update); threads.append(thread1)
for t in threads:
    t.start()




client.polling(none_stop=True, interval=0)
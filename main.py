import telebot
from scapy.all import ARP, sniff
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
from paswords import *

token = lemonade
# token = major_suetolog

bot = telebot.TeleBot(token)

users_list = []
cash_list = []
main_dict = {'fa:95:5b:62:0a:a2': 'мой', '26:59:62:b9:26:31': 'мой'}
admin_id = admin_id


def handle_arp(pkt):
    global cash_list, users_list
    if ARP in pkt and pkt[ARP].op == 2:
        if pkt[ARP].hwsrc in cash_list:
            pass
        elif pkt[ARP].hwsrc in users_list:
            pass
        else:
            users_list.append(pkt[ARP].hwsrc)
            cash_list.append(pkt[ARP].hwsrc)
            if pkt[ARP].hwsrc in main_dict:
                print(f'{main_dict[pkt[ARP].hwsrc]} подключился')
                bot.send_message(admin_id, f'{main_dict[pkt[ARP].hwsrc]} подключился')
            else:
                print(f'{pkt[ARP].hwsrc} подключился')
                bot.send_message(admin_id, f'{pkt[ARP].hwsrc} подключился')


def check_users():
    global cash_list, users_list
    print('check_users')
    for i in users_list:
        if i in cash_list:
            pass
        else:
            if i in main_dict:
                print(f'{main_dict[i]} отключился')
                bot.send_message(admin_id, f'{main_dict[i]} отключился')
                users_list.remove(i)
            else:
                print(f'{i} отключился')
                bot.send_message(admin_id, f'{i} отключился')
                users_list.remove(i)
    cash_list.clear()


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, ('Основные команды поддерживаемые ботом:\n'
                                             '/start - инициализация бота\n'
                                             '/help - справка по боту\n'
                                             '/monitor - вывод списка подключенных к wifi'))


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '''Бот инициализирован.
/help - справка по боту''')


@bot.message_handler(commands=['monitor'])
def monitor(message):
    print_list = []
    for i in users_list:
        if i in main_dict:
            print_list.append(f'MAC: {i} - владелец: {main_dict[i]}')
        else:
            print_list.append(f'MAC: {i} - владелец: неизвестно')
    bot.send_message(message.chat.id, f'{print_list}')


def monitoring():
    while True:
        sniff(prn=handle_arp, store=0, iface="Ethernet 2")
        print('monitor')


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_users, "interval", seconds=10)
    scheduler.start()
    monitor_process = multiprocessing.Process(target=monitoring)
    monitor_process.start()
    bot.infinity_polling()
import telebot
from scapy.all import ARP, sniff
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
from paswords import *
from database import *

token = lemonade
# token = major_suetolog

bot = telebot.TeleBot(token)

admin_id = admin_id


def handle_arp(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):
        if database().search_in_table(table='cash', search_mac=pkt[ARP].hwsrc)[0] is True:
            pass
        elif database().search_in_table(table='users', search_mac=pkt[ARP].hwsrc)[0] is True:
            database().update_table("cash", pkt[ARP].hwsrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
        elif database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[0] is True:
            database().update_table("users", pkt[ARP].hwsrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            database().update_table("cash", str(pkt[ARP].hwsrc),
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            print(f'{database().search_in_table(table="main", search_mac=pkt[ARP].hwsrc)[1]} '
                  f'подключился c мак адресом: {pkt[ARP].hwsrc}')
            bot.send_message(admin_id, f'{database().search_in_table(table="main", search_mac=pkt[ARP].hwsrc)[1]} '
                                       f'подключился c мак адресом: {pkt[ARP].hwsrc}')
        else:
            database().update_table("users", pkt[ARP].hwsrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            database().update_table("cash", pkt[ARP].hwsrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            print(f'неизвестное устройство подключился c мак адресом: {pkt[ARP].hwsrc}')
            bot.send_message(admin_id, f'неизвестное устройство подключился c мак адресом: {pkt[ARP].hwsrc}')


def check_users():
    print('check_users')
    for i in database().return_all('users'):
        if i in database().return_all('cash'):
            pass
        else:
            # if mac == "('',)":
            #     pass
            print(f'{i[1]} c мак адресом {i[0]} отключился')
            bot.send_message(admin_id, f'{i[1]} c мак адресом {i[0]} отключился')
            database().delete_user('users', i[0])
    database().delete_all('cash')


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
    for i in database().return_all('users'):
        bot.send_message(message.chat.id, f'MAC: {i[0]} - владелец: {i[1]}')


def monitoring():
    while True:
        sniff(prn=handle_arp, filter='arp', store=0, iface="Ethernet 2")
        print('monitor')


if __name__ == '__main__':
    database().delete_all('cash')
    database().delete_all('users')
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_users, "interval", seconds=30)
    scheduler.start()
    monitor_process = multiprocessing.Process(target=monitoring)
    monitor_process.start()
    bot.infinity_polling()

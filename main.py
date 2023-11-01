import telebot
import re
from scapy.all import ARP, sniff
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
from scapy.layers.l2 import Ether
from scapy.sendrecv import srp

from paswords import *
from database import *

token = lemonade
# token = major_suetolog
i_face = "Беспроводная сеть 2"
bot = telebot.TeleBot(token)
#filterlist = ['54:48:e6:ed:80:76', '00:00:00:00:00:00']

admin_id = admin_id


def handle_arp(pkt):
    if ARP in pkt and pkt[ARP].op in (1, 2):
        if database().search_in_table(table='users', search_mac=pkt[ARP].hwsrc)[0] is True:
            pass
        elif database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[0] is True:
            database().update_table("users", pkt[ARP].hwsrc, pkt[ARP].psrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            print(f'{database().search_in_table(table="main", search_mac=pkt[ARP].hwsrc)[1]} '
                  f'подключился c мак адресом: {pkt[ARP].hwsrc}')
            bot.send_message(admin_id, f'🟢 {database().search_in_table(table="main", search_mac=pkt[ARP].hwsrc)[1]} '
                                       f' подключился c мак адресом: {pkt[ARP].hwsrc}')
        else:
            database().update_table("users", pkt[ARP].hwsrc, pkt[ARP].psrc,
                                    database().search_in_table(table='main', search_mac=pkt[ARP].hwsrc)[1])
            print(f'неизвестное устройство подключился c мак адресом: {pkt[ARP].hwsrc}')
            bot.send_message(admin_id, f'🟢 неизвестное устройство подключился c мак адресом: {pkt[ARP].hwsrc}')


def check_users():
    print('check_users')
    for i in database().return_all('users'):
        # if i[0] in filterlist:
        #     pass
        # elif get_mac_by_ip(i[1]) is True:
        if get_mac_by_ip(i[0], i[1]) is True:
            pass
        
        else:
            print(f'{i[2]} c мак адресом {i[0]} отключился')
            bot.send_message(admin_id, f'🔴 {i[2]} c мак адресом {i[0]} отключился')
            database().delete_user('users', i[0])


# def get_mac_by_ip(ip_address):
#     arp = ARP(pdst=ip_address)
#     ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Широковещательный запрос
#     packet = ether / arp
#
#     result = srp(packet, timeout=3, verbose=0)[0]
#
#     for sent, received in result:
#         return True
#     return False


def get_mac_by_ip(mac, ip):
    # Создаем ARP-запрос для проверки IP-адреса
    arp = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Широковещательный запрос
    packet = ether/arp
    # Отправляем ARP-запрос и получаем ответы
    result = srp(packet, timeout=3, iface=i_face, verbose=False)
    responses = result[0]  # Получаем первый элемент кортежа, который содержит ответы
    print(result)
    print(responses)
    if responses:
        arp_response = responses[0][1]  # Получаем второй элемент кортежа, который содержит ответ ARP
        print(arp_response)
        # пример ответа: Ether / ARP is at 00:10:75:40:14:f1 says 192.168.1.66 / Padding
        mac_pattern = r'(\b[0-9A-Fa-f:]+\b)'
        mac_address = re.search(mac_pattern, str(arp_response)).group()
        if mac == mac_address:
            return True
        else:
            return False

    else:
        return False


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
    for i in database().return_all('users'):
        bot.send_message(message.chat.id, f'MAC: {i[0]} - владелец: {i[1]}')


def monitoring():
    while True:
        sniff(prn=handle_arp, filter='arp', store=0, iface=i_face)
        print('monitor')


if __name__ == '__main__':
    database().delete_all('users')
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_users, "interval", seconds=30)
    scheduler.start()
    monitor_process = multiprocessing.Process(target=monitoring)
    monitor_process.start()
    bot.infinity_polling()

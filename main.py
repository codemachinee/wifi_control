import telebot
from scapy.all import ARP, sniff
import multiprocessing
from apscheduler.schedulers.background import BackgroundScheduler
import subprocess

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
        ping = ping_cheking(i[1])
        if ping == 1:
            pass
        
        elif ping == 0:
            print(f'{i[2]} c мак адресом {i[0]} отключился')
            bot.send_message(admin_id, f'🔴 {i[2]} c мак адресом {i[0]} отключился')
            database().delete_user('users', i[0])
        elif ping == 2:
            print(f'отсутствует соединение')
            bot.send_message(admin_id, f'отсутствует соединение')


def ping_cheking(target_ip):
# Выполняем пинг
    ping_result = subprocess.run(["ping", '-n', "2", target_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True)
# Получаем код завершения пинга
    ping_exit_code = ping_result.stdout.encode('windows-1251').decode('cp866')
    print(ping_exit_code)
    if ping_exit_code.count('Заданный узел недоступен.') >= 1:
        return 0
    elif ping_exit_code.find('Превышен интервал ожидания для запроса.') != -1:
        return 1
    elif ping_exit_code.find('число байт=') != -1:
        return 1
    else:
        return 2


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
        bot.send_message(message.chat.id, f'MAC: {i[0]} - владелец: {i[2]}')


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

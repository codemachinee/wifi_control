# from scapy.all import IP, ICMP, sr1
#
# # IP-адрес, на который вы хотите выполнить пинг
# target_ip = "192.168.1.112"
#
# # Создаем ICMP-пакет (пинг-запрос)
# ping_packet = IP(dst=target_ip) / ICMP()
#
# # Отправляем пакет и ждем ответа
# response = sr1(ping_packet, timeout=2, verbose=True)
#
# # Проверяем, получен ли ответ
# if response:
#     print(f"Пинг на {target_ip} успешен. Получен ответ от {response}")
# else:
#     print(f"Пинг на {target_ip} не удался. Хост не отвечает.{response}")
import encodings
import subprocess

# IP-адрес, который вы хотите проверить
target_ip = "192.168.1.110"

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


# Выводим код завершения
def answer():
    answer = ping_cheking(target_ip)
    if answer == 0:
        print('устройство не в сети')
    elif answer == 1:
        print('устройство в сети')
    else:
        print('отсутствует соединение')



answer()
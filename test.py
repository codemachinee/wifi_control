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

import subprocess

# IP-адрес, который вы хотите проверить
target_ip = "192.168.1.112"

# Выполняем пинг
ping_result = subprocess.run(["ping", '-n', "2", target_ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Получаем код завершения пинга
ping_exit_code = ping_result.returncode

# Выводим код завершения
print(f"Код завершения пинга: {ping_exit_code}")


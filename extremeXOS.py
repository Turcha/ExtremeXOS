import paramiko
from telnetlib import Telnet
import time

# username - имя пользователя, password - пароль пользователя
# max_bytes - размер данных, command - команда для исполнения
# second_output - время для вывода, all_list - Вывод полного списка сразу или нет


class ExtremeXOS:

    # Входные данные для подключения к оборудованию
    def __init__(self, ipaddress, port, username, password):
        # Ip адрес устройства
        self.__ipaddress = ipaddress
        # Имя пользователя
        self.__username = username
        # Пароль пользователя
        self.__password = password
        # Порт для подключения telnet-23, ssh-22
        self.__port = port
        # Создаем подключение
        if self.__port == 22:
            # Создаем объект для подключение по SSH
            self.__ssh = paramiko.SSHClient()
        elif self.__port == 23:
            # Создаем объект для подключение по Telnet
            self.__telnet = Telnet()
        # Максимальное считывание байтов
        self.__max_bytes = 60000
        # Время вывода
        self.__second_output = 0.5

    # Подключение к устройству
    def connect_device(self, all_list=True):
        # Подключаемся по ssh
        if self.__port == 22:
            # Подтверждаем ключи от хостов автоматически
            self.__ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Подключаемся к устройству
            self.__ssh.connect(self.__ipaddress, self.__port, self.__username, self.__password, look_for_keys=False, allow_agent=False)
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet.open(self.__ipaddress)

    # Исполняемые команды для подключенных по telnet
    def __telnet_command(self, command):
        # Считываем строку
        self.__telnet.read_until(b"login: ")
        # Ввод логина
        self.__telnet.write(self.__username.encode('utf-8') + b"\n")
        # Даем время на запись
        time.sleep(self.__second_output)
        # Считываем строку
        self.__telnet.read_until(b"password: ")
        # Ввод пароля
        self.__telnet.write(self.__password.encode('utf-8') + b"\n")
        # Даем время на запись
        time.sleep(self.__second_output)
        self.__telnet.read_until(b"# ")
        self.__telnet.write(command + b"\n")
        time.sleep(self.__second_output)
        self.__telnet.read_until(b"# ")
        self.__telnet.write(b"save conf\n")
        time.sleep(self.__second_output)
        self.__telnet.read_until(b") ")
        self.__telnet.write(b"y\n")
        time.sleep(self.__second_output)
        self.__telnet.write(b'exit\n')

    # Исполняемые команды для подключенных по ssh
    def __ssh_command(self, command):
        # invoke_shell - позволяет установить интерактивную сессию SSH с сервером
        with self.__ssh.invoke_shell() as cl_ssh:
            time.sleep(self.__second_output)
            # Отправляем данные
            cl_ssh.send(command)
            time.sleep(self.__second_output)
            cl_ssh.send("save conf\n")
            cl_ssh.send("y\n")
            time.sleep(self.__second_output)

    # Создание vlan's
    def create_vlan(self, name, number):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"create vlan {name} tag {number}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("create vlan {0} tag {1}".format(name, number).encode("utf8"))

    # Удаление vlan's
    def delete_vlan(self, number):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"delete vlan {number}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("delete vlan {0}".format(number).encode("utf8"))

    # Установить vlan на интерфейсе
    def install_vlan_interface(self, port, mode, vlans:[]):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"configure vlan {vlans} add port {port} {mode}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("configure vlan {0} add port {1} {2}".format(vlans, port, mode).encode("utf8"))

    # Удалить vlan с интерфейса
    def delete_vlan_interface(self, port, vlan):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"configure vlan {vlan} delete port {port}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("configure vlan {0} delete port {1}".format(vlan, port).encode("utf8"))

    # Отключить порт (передачу данных)
    def down_port(self, port):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"disable port {port}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("disable port {0}".format(port).encode("utf8"))

    # Включить порт (передачу данных)
    def up_port(self, port):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"enable port {port}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("enable port {0}".format(port).encode("utf8"))

    # Отключить порт (по питанию poe)
    def power_down_port(self, port):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"disable inline-power ports {port}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("disable inline-power ports {0}".format(port).encode("utf8"))

    # Включить порт (по питанию poe)
    def power_up_port(self, port):
        # Подключаемся по ssh
        if self.__port == 22:
            self.__ssh_command(f"enable inline-power ports {port}\n")
        # Подключаемся по telnet
        elif self.__port == 23:
            self.__telnet_command("enable inline-power ports {0}".format(port).encode("utf8"))

    # Закрытие подключение к устройству
    def close_device(self):
        # Закрываем порт 22
        if self.__port == 22:
            self.__ssh.close()
        # Закрываем порт 23
        elif self.__port == 23:
            self.__telnet.close()

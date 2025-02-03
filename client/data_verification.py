import asyncio

from private_data import server_address, server_port
from config import max_bytes_to_name


async def get_address_port():
    """Функция для получения актуального адреса и порта сервера"""

    while True:
        # запрашиваем данные (адрес и порт сервера) для подключения
        host_address = input('Для поключения к чату введите, пожалуйста, следующие данные: '
                            '\nАдрес сервера (например, 127.0.0.1): ')
        host_port = input("Порт сервера (например, 8888): ")

        # проверяем данные, введенные пользователем, в случае ошибки - запрашиваем данные еще раз
        if host_address != server_address or host_port != server_port:
            print('Неправильный адрес сервера или порта. Повторите попытку.\n')
        else:
            return host_address, host_port


async def get_unique_name(host_address, host_port):
    """Функция для получения уникального имени клиента"""

    while True:
        reader, writer = await asyncio.open_connection(host_address, host_port)  # устанавливаем соединение с сервером
        name = input("Ваше имя: ")  # запрашиваем имя
        writer.write(name.encode())  # отправляем имя на сервер
        await writer.drain()  # ждем, пока сообщение не будет отправлено

        data = await reader.read(max_bytes_to_name)  # получаем ответ от сервера
        message = data.decode().strip()  # декодируем полученные байты в строку и убираем лишние пробелы

        # если введеное пользователем имя уже существует в системе,
        # выводим соответствующее сообщение и запрашиваем имя еще раз
        if message == "name is not unique":
            print("Это имя уже занято. Пожалуйста, выберите другое имя.\n")
        else:
            print(f"\n{name}, добро пожаловать в чат!" 
                  f"\nДля выхода из чата - напишите exit.\n")  # если имя уникально - приветствуем пользователя в чате
            return reader, writer

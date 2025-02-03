import asyncio

from client.data_verification import get_address_port, get_unique_name
from client.io_operation import read_messages, write_messages


async def main():
    """Основная функция для подключения клиента к серверу"""

    # получаем адрес и порт сервера
    host_address, host_port = await get_address_port()

    # проверяем уникальность имени клиента и устанавливаем соединение с сервером
    # возвращаем объекты reader и writer для дальнейшего общения
    reader, writer = await get_unique_name(host_address, host_port)

    # Запускаем две асинхронные задачи
    asyncio.create_task(read_messages(reader))  # чтение сообщений
    await write_messages(writer)  # отправка сообщений


if __name__ == '__main__':
    asyncio.run(main())  # запуск основной асинхронной функции
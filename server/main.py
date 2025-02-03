import asyncio
from server.client_handler import handle_client
from private_data import server_address, server_port


async def main():
    """Основная функция для запуска сервера и обработки подключений."""

    host_address = server_address  # адрес сервера
    host_port = server_port  # порт сервера

    server = await asyncio.start_server(handle_client, host_address, host_port)  # создаем сервер
    addr = server.sockets[0].getsockname()  # получаем адрес и порт сервера
    print(f'Сервер запущен на {addr}')  # выводим сообщение о запуске сервера

    async with server:
        await server.serve_forever()  # запускаем сервер и ждем подключения клиентов


if __name__ == '__main__':
    asyncio.run(main())  # запуск основной асинхронной функции
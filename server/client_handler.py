from server.broadcast import broadcast, clients
from config import max_bytes_to_name, max_bytes_to_message


async def handle_exit(writer, name):
    """Функция для обработки выхода пользователя"""

    print(f"Пользователь {name} покинул чат.")  # выводим сообщение на сервере
    del clients[name]  # удаляем клиента из списка

    try:
        writer.close()  # закрываем соединение с клиентом
        await writer.wait_closed()  # ждем, пока соединение полностью закроется
    except (ConnectionResetError, ConnectionAbortedError):  # обрабатываем возникающие ошибки
        pass

    await broadcast(f"Пользователь {name} покинул чат.")  # выводим сообщение всем подключенным клиентам


async def check_unique_name(name, clients, writer):
    """Функция для проверки уникальности имени в списке клиентов"""

    if name in clients:
        writer.write("name is not unique".encode())  # отправляем сообщение о том, что имя занято
        await writer.drain()  # ждем, пока сообщение не будет отправлено
        writer.close()  # закрываем соединение с этим клиентом
        return False  # имя не уникально
    return True  # имя уникально


async def handle_client(reader, writer):
    """Функция обработки клиента: подключение, получение и отправка сообщений"""

    # получаем имя пользователя от клиента
    data = await reader.read(max_bytes_to_name)  # чтение данных от клиента
    name = data.decode().strip()  # декодируем полученные байты в строку и убираем лишние пробелы

    # проверка уникальности имени
    if not await check_unique_name(name, clients, writer):
        return  # если имя не уникально, выходим из функции

    clients[name] = writer  # добавляем нового клиента в словарь
    print(f"Пользователь {name} присоединился к чату.")  # выводим сообщение на сервере

    await broadcast(f"Пользователь {name} подключился к чату.")  # выводим сообщение всем подключенным клиентам

    try:
        while True:
            data = await reader.read(max_bytes_to_message)  # читаем сообщение от клиента
            if not data:
                raise ConnectionResetError()  # если клиент закрыл терминал, вызываем исключение

            message = data.decode().strip()  # декодируем сообщение и убираем лишние пробелы

            if message.lower().strip() == 'exit':  # если клиент написал 'exit', завершаем сессию
                # вызываем функцию обработки вызода клиента для оповещения пользователей и удаления клиента из словаря
                await handle_exit(writer, name)
                break  # выходим из цикла
            else:
                print(f"[{name}]: {message}")  # выводим сообщение на сервере
                await broadcast(f"[{name}]: {message}", exclude=writer)  # выводим сообщение всем подключенным клиентам

    except (ConnectionResetError, ConnectionAbortedError):  # Обрабатываем возможные ошибки отмены
        await handle_exit(writer, name)
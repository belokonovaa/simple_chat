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


async def check_private_name(message, writer, name):
    """Функция для обработки приватных сообщений"""

    parts = message.split(' ', 1)  # делим приватное сообщение - на имя пользователя и само сообщение

    # если количество частей строго больше 1, работаем с отправкой приватного сообщения,
    # если нет - выводим предупреждение о невозможности отправить пустое сообщение
    if len(parts) > 1:
        private_user = parts[0][1:]  # извлекаем имя пользователя после '@'
        private_message = parts[1]  # извлекаем сообщение

        # если имя пользовател, указанное после @, совпадает с именем отправителя
        # выводим предупреждение о невозможности отправить приватное сообщение себе
        if private_user == name:
            writer.write("Вы не можете отправить приватное сообщение себе.\n".encode())
            await writer.drain()
            return

        # если пользователь есть среди подключенных клиентов - отправляем ему приватное сообщение,
        # если нет - выводим предупреждение об отсутствиии такого пользователя среди подключенных клентов
        if private_user in clients: # Проверка, существует ли такой пользователь в списке
            private_writer = clients[private_user]
            private_writer.write(f"(Приватное сообщение от {name}): {private_message}\n".encode())
            await private_writer.drain()
        else:
            writer.write(f"Пользователь {private_user} не найден.\n".encode())
            await writer.drain()
    else:
        writer.write("Вы не можете отправить пустое приватное сообщение.\n".encode())
        await writer.drain()


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

            if message.startswith('@'):  # если клиент начал сообщение с '@',
                # вызываем функцию для обработки приватного сообщения
                await check_private_name(message, writer, name)
            else:
                print(f"[{name}]: {message}")  # выводим сообщение на сервере
                await broadcast(f"[{name}]: {message}", exclude=writer)  # выводим сообщение всем подключенным клиентам

    except (ConnectionResetError, ConnectionAbortedError):  # Обрабатываем возможные ошибки отмены
        await handle_exit(writer, name)
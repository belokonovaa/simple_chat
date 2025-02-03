import asyncio

from config import max_bytes_to_message


async def read_messages(reader):
    """Функция для чтения сообщений от сервера"""

    while True:
        try:
            data = await reader.read(max_bytes_to_message)  # чтение данных
            if not data:  # если данных нет, выходим из цикла
                break
            print(data.decode(), end="")  # если данные есть, декодируем их и выводим пользователям
        except asyncio.CancelledError:
            break  # если получили ошибку, закрываем соединение


async def write_messages(writer):
    """Функция для чтения сообщений от пользователей"""

    while True:
        message = await asyncio.to_thread(input, '')  # ожидает сообщение от пользователя

        # если пользователь хочет отправить пустое сообщение, выводим предупреждение
        if not message.strip():
            print('Вы не можете отправить пустое сообщение.')
            continue

        if message.lower().strip() == 'exit':  # если пользователь ввел "exit", отправляем сообщение о выходе
            writer.write(f"{message}\n".encode())
            await writer.drain()  # ждем, пока сообщение не будет отправлено
            print(f'Вы покинули чат.')  # сообщаем пользователю, что он вышел
            break  # выходим из цикла

        if message.startswith('@'): # если пользователь начал сообщение с '@', отправляем приватное сообщение
            writer.write(f"{message}\n".encode())
            await writer.drain()
            continue

        else:
            writer.write(f"{message}\n".encode())  # Отправляем обычное сообщение
            await writer.drain()  # ждем, пока сообщение не будет отправлено





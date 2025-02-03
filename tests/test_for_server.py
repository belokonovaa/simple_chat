import unittest
from unittest.mock import MagicMock
from server.client_handler import check_unique_name, handle_exit
from server.broadcast import broadcast


class TestServerFunction(unittest.TestCase):

    def setUp(self):
        """Функция для подготовки к проведению тестов: очищение словаря клиентов перед каждым запуском теста"""

        global clients
        clients = {}

    async def test_check_unique_name(self):
        """Тест для проверки уникальности имени - если имя уникально, должно вернуться True"""

        mock_writer = MagicMock()  # создаем мок (заглушку), имитирующий объект writer

        result = await check_unique_name('new_client', clients, mock_writer)

        self.assertTrue(result)

    async def test_check_not_unique_name(self):
        """Тест для проверки уникальности имени - если имя уже существует, должно вернуться False"""

        mock_writter = MagicMock()
        clients['existing_name'] = mock_writter

        result = await check_unique_name('existing_name', clients, mock_writter)

        self.assertFalse(result)

    async def test_broadcast(self):
        """Тест для проверки отправки сообщений всем пользователям чата, кроме отправителя"""

        mock_writer1 = MagicMock()
        mock_writer2 = MagicMock()

        clients['client1'] = mock_writer1
        clients['client2'] = mock_writer2

        await broadcast('Hi everyone!', exclude=mock_writer1)

        mock_writer1.write.assert_not_called()
        mock_writer2.write.assert_called_with('Hi everyone!'.encode())

    async def test_handle_exit(self):
        """Тест для проверки удаления пользователя из списка клиентов"""

        mock_writer = MagicMock()
        clients['client_1'] = mock_writer

        await handle_exit(mock_writer, 'client_1')

        self.assertNotIn('client_1', clients)


if __name__ == '__main__':
    unittest.main()
import sqlite3, os
from src.helpers import get_config_path
from sqlite3 import connect
from datetime import datetime

from src.bot_controller import AbstractBotController, BotController
from src.web_socket_message_handlers.command_processors.abstract_command_processor import AbstractCommandProcessor
from src.web_socket_message_handlers.objects.user_input import UserInput
from src.web_socket_message_handlers.objects.push_message import PushMessage


class CharlixcxCommandProcessor(AbstractCommandProcessor):
    def __init__(self, bot_controller: AbstractBotController = BotController.get_instance()):
        self.__bot_controller = bot_controller

    @property
    def keyword(self) -> str:
        return 'charlixcx'

    @property
    def help(self) -> str:
        return 'Bring me the pictures of Charli XCX immediately!'

    def process(self, pushMessage: PushMessage, userInput: UserInput) -> None:
        path = os.path.join(get_config_path(), 'gifs.sqlite')
        connection = connect(path)
        connection.execute('''
            CREATE TABLE IF NOT EXISTS charlixcx (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                publisher_id TEXT,
                url TEXT
        )''')
        if userInput.arguments:
            if userInput.args_check('add', 0):
                if userInput.args_get(1).startswith(('http://','https://')) and userInput.args_get(1).endswith('.gif'):
                    gif_url = userInput.args_get(1)
                    self.add(connection, gif_url, pushMessage.user.uri)
                    self.__bot_controller.chat('Gif has been added :+1:')            
                else:
                    self.__bot_controller.chat('Incorrect link')
        else:
            self.__bot_controller.chat(self.get_random(connection)) 
        connection.close()

    def add(self, connection: sqlite3.Connection, url: str, publisher_id: str) -> None:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO charlixcx (timestamp, publisher_id, url) VALUES (?, ?, ?)',
        (datetime.now().timestamp(), publisher_id, url))
        connection.commit()
        cursor.close()
        
    def get_random(self, connection: sqlite3.Connection) -> str:
        cursor = connection.cursor()
        result = cursor.execute('SELECT url FROM charlixcx ORDER BY RANDOM() LIMIT 1').fetchall()
        cursor.close()
        return str(result[0][0])

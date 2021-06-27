import random, sqlite3, os, sys
from src.helpers import get_main_dir
from sqlite3 import connect
from datetime import datetime
from typing import Optional, List

from src.bot_controller import AbstractBotController, BotController
from src.web_socket_message_handlers.command_processors.abstract_command_processor import AbstractCommandProcessor


class CharlixcxCommandProcessor(AbstractCommandProcessor):
    def __init__(self, bot_controller: AbstractBotController = BotController.get_instance()):
        self.__bot_controller = bot_controller

    @property
    def keyword(self) -> str:
        return 'charlixcx'

    @property
    def help(self) -> str:
        return 'Bring me the pictures of Charli XCX immediately!'

    def process(self, user_id: str, payload: Optional[str]) -> None:
        path = os.path.join(get_main_dir(), '..', 'config', 'gifs.sqlite')
        connection = connect(path)
        connection.execute('''
            CREATE TABLE IF NOT EXISTS charlixcx (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp INTEGER,
                publisher_id TEXT,
                url TEXT
        )''')
        if payload != None:
            payload = payload.strip().split()
            if payload[0] in {'add'}:
                if len(payload) > 1 and payload[1] != None:
                    if payload[1].startswith(('http://','https://')) and payload[1].endswith('.gif'):
                        gif_url = payload[1]
                        self.add(connection, gif_url, user_id)
                        self.__bot_controller.chat('Gif has been added :+1:')            
                    else:
                        self.__bot_controller.chat('Usage: /charlixcx add [url]')
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

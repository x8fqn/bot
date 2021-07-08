import os, logging, shlex
from typing import List, Dict, Union

from src.web_socket_message_handlers.command_processors.abstract_command_processor import AbstractCommandProcessor
from src.web_socket_message_handlers.command_processors.command_processors import command_processors
from src.web_socket_message_handlers.command_processors.help import HelpCommandProcessor
from src.web_socket_message import WebSocketMessage
from src.web_socket_message_handlers.abstract_web_socket_message_handler import AbstractWebSocketMessageHandler
from src.bot_controller import AbstractBotController, BotController


class PushMessageHandler(AbstractWebSocketMessageHandler):
    def __init__(self, bot_controller: AbstractBotController = BotController.get_instance(),
                 _command_processors: List[AbstractCommandProcessor] = None):
        self.__bot_controller = bot_controller
        self.__command_processors: Dict[str, AbstractCommandProcessor] = {
            x.keyword: x for x in _command_processors or (command_processors + [HelpCommandProcessor()])
        }

    @property
    def message_label(self) -> str:
        return 'push-message'

    def handle(self, message: WebSocketMessage) -> None:
        payload = message.payload
        message = payload['message'].strip()
        user_id = self.__getUserID(payload)
        if not self.__isValidUser(user_id): return
        if not self.__isValidMessage(message): return

        message_parts = message.split(' ', 1)
        keyword = message_parts[0].lower().split('/', 1)[-1]
        payload = None if len(message_parts) == 1 else self.__payloadProcess(message_parts[1])

        logging.info('%s called by %s' % (repr(message_parts), user_id))
        command_processor = self.__command_processors.get(keyword)
        if command_processor:
            command_processor.process(user_id, payload)

    def __getUserID(self, payload: str):
        return payload.get('user', {}).get('id', None)

    def __isValidUser(self, user_id: str) -> bool:
        if user_id is None or user_id == self.__config.get('spotify_user_id'): 
            return False
        else: return True

    def __payloadProcess(self, payload: str) -> Union[str, List[str]]:
        if payload.find(' ') == -1: return payload
        else: return shlex.split(payload)

    def __isValidMessage(self, message: str) -> bool:
        if not (message.startswith('/') and len(message) > 1):
            return False
        else: return True

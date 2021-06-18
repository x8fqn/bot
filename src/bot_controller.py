from abc import ABC, abstractmethod
from typing import List, Optional, Union

from src.configuration import AbstractConfiguration, Configuration
from src.helpers import get_bot_user
from src.web_socket_client import AbstractWebSocketClient, WebSocketClient
from src.web_socket_message import WebSocketMessage


class AbstractBotController(ABC):
    @abstractmethod
    def chat(self, message: Union[str, List[str]]) -> None:
        pass
    
    @abstractmethod
    def interroom_chat(self, room_id: str, username: str, message: str) -> None:
        pass
    
    @abstractmethod
    def whisper(self, message: str, recipient: dict) -> None:
        pass

    @abstractmethod
    def dope(self) -> None:
        pass

    @abstractmethod
    def nope(self) -> None:
        pass

    @property
    @abstractmethod
    def star(self) -> None:
        pass

    @property
    @abstractmethod
    def doped(self) -> bool:
        pass

    @property
    @abstractmethod
    def noped(self) -> bool:
        pass

    @property
    @abstractmethod
    def starred(self) -> bool:
        pass
    
    @abstractmethod
    def reset_vote(self) -> None:
        pass


class BotController(AbstractBotController):
    __instance: Optional['BotController'] = None

    def __init__(self, config: AbstractConfiguration = Configuration('bot_main', 'config'),
                 web_socket_client: AbstractWebSocketClient = WebSocketClient.get_instance()):
        if BotController.__instance:
            raise Exception('Use get_instance() instead!')
        self.__config = config
        self.__web_socket_client = web_socket_client
        self.__current_track: Optional[dict] = None
        self.__doped: bool = False
        self.__noped: bool = False
        BotController.__instance = self

    @staticmethod
    def get_instance() -> 'BotController':
        if BotController.__instance is None:
            BotController()
        return BotController.__instance

    def chat(self, message: Union[str, List[str]]) -> None:
        lines = message if isinstance(message, list) else [message]
        payload = {
            'roomId': self.__config.get()['jqbx_room_id'],
            'user': get_bot_user(self.__config.get()),
            'message': {
                'message': ' <br/> '.join(lines),
                'user': get_bot_user(self.__config.get()),
                'selectingEmoji': False
            }
        }
        self.__web_socket_client.send(WebSocketMessage(label='chat', payload=payload))

    def interroom_chat(self, room_id: str, username: str, message: str) -> None:
        payload = {
            'roomId': room_id,
            'user': get_bot_user(self.__config.get()),
            'message': {
                'message': message,
                'user': get_bot_user(self.__config.get()),
                'selectingEmoji': False
            }
        }
        payload['message']['user']['username'] = username
        self.__web_socket_client.send(WebSocketMessage(label='chat', payload=payload))

    def whisper(self, message: str, recipient: dict) -> None:
        bot_user = get_bot_user(self.__config.get())
        payload = {
            'roomId': self.__config.get()['jqbx_room_id'],
            'user': bot_user,
            'message': {
                'message': '%s' % message,
                'user': get_bot_user(self.__config.get()),
                'recipients': [
                    recipient,
                    bot_user
                ],
                'selectingEmoji': False
            }
        }
        self.__web_socket_client.send(WebSocketMessage(label='chat', payload=payload))

    def dope(self) -> None:
        if self.__doped or self.__noped:
            return
        self.__web_socket_client.send(WebSocketMessage(label='thumbsUp', payload={
            'roomId': self.__config.get()['jqbx_room_id'],
            'user': get_bot_user(self.__config.get())
        }))
        self.__doped = True

    def nope(self) -> None:
        if self.__doped or self.__noped:
            return
        self.__web_socket_client.send(WebSocketMessage(label='thumbsDown', payload={
            'roomId': self.__config.get()['jqbx_room_id'],
            'user': get_bot_user(self.__config.get())
        }))
        self.__noped = True

    def star(self) -> None:
        if self.__starred:
            return
        self.__web_socket_client.send(WebSocketMessage(label='starTrack', payload={
            'roomId': self.__config.get()['jqbx_room_id'],
            'user': get_bot_user(self.__config.get())
        }))
        self.__starred = True

    @property
    def doped(self) -> bool:
        return self.__doped

    @property
    def noped(self) -> bool:
        return self.__noped

    @property
    def starred(self) -> bool:
        return self.__starred

    def reset_vote(self) -> None:
        self.__doped = False
        self.__noped = False
        self.__starred = False

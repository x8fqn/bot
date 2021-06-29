import logging
from src.room_state import AbstractRoomState, RoomState
from src.web_socket_message import WebSocketMessage
from src.web_socket_message_handlers.abstract_web_socket_message_handler import AbstractWebSocketMessageHandler
from src.configuration import AbstractConfiguration, Configuration
from src.web_socket_message_handlers.command_processors.first import FirstProcessor
from src.web_socket_message_handlers.command_processors.abstract_command_processor import AbstractCommandProcessor

class PlayTrackHandler(AbstractWebSocketMessageHandler):
    def __init__(self, room_state: AbstractRoomState = RoomState.get_instance(),
                first_processor: AbstractCommandProcessor = FirstProcessor()):
        self.__room_state = room_state
        self.__config: AbstractConfiguration = Configuration('bot_main')
        self.__first_processor = first_processor

    @property
    def message_label(self) -> str:
        return 'play-track'

    def handle(self, message: WebSocketMessage) -> None:
        self.__room_state.set_current_track(message.payload)
        logging.info('Track playing now: %s - %s' % (
                self.__room_state.current_track['name'],
                ", ".join([i['name'] for i in self.__room_state.current_track['artists']])
                ))
        if self.__config.update('auto-first') == True:
            self.__first_processor.process(self.__room_state.djs[0]['id'], None)
            pass

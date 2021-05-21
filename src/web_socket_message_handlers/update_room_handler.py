from typing import List

from src.bot_controller import AbstractBotController, BotController
from src.env import Environment, AbstractEnvironment
from src.room_state import AbstractRoomState, RoomState
from src.web_socket_message import WebSocketMessage
from src.web_socket_message_handlers.abstract_web_socket_message_handler import AbstractWebSocketMessageHandler
from src.logger import AbstractLogger, Logger


class UpdateRoomHandler(AbstractWebSocketMessageHandler):
    def __init__(self, bot_controller: AbstractBotController = BotController.get_instance(),
                 room_state: AbstractRoomState = RoomState.get_instance(),
                 env: AbstractEnvironment = Environment(),
                 logger: AbstractLogger = Logger()):
        self.__bot_controller = bot_controller
        self.__room_state = room_state
        self.__env = env
        self.__logger = logger

    @property
    def message_label(self) -> str:
        return 'update-room'

    def handle(self, message: WebSocketMessage) -> None:
        payload = message.payload
        self.__update_mod_ids(payload)
        self.__update_users(message.payload)
        self.__update_track(payload)
        self.__update_room_title(payload)

    def __update_mod_ids(self, payload: dict) -> None:
        admins = payload.get('admin', [])
        mods = payload.get('mods', [])
        if admins + mods:
            self.__room_state.set_mod_ids([x.split(':')[-1] for x in list(set(admins + mods))])

    def __update_users(self, payload: dict) -> None:
        users: List[dict] = payload.get('users', [])
        djs: List[dict] = payload.get('djs', [])
        if self.__room_state.users:
            new_users = [
                x for x in users
                if x['id'] != self.__env.get_spotify_user_id()
                   and x['id'] not in [y['id'] for y in self.__room_state.users]
            ]
        if 'users' in payload:
            self.__room_state.set_users(users)
        if 'djs' in payload:
            self.__room_state.set_djs(djs)

    def __update_track(self, payload: dict) -> None:
        tracks = payload.get('tracks', [])
        if tracks:
            self.__room_state.set_current_track(tracks[0])

    def __update_room_title(self, payload: dict) -> None:
        room_title = payload.get('title')
        if room_title:
            self.__room_state.set_room_title(room_title)
            self.__logger.info('Room title changed: %s' % room_title)

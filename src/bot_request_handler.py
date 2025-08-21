import os

from dotenv import load_dotenv
from abc import ABC, abstractmethod
from fastapi import Depends

from src.schemas import BotMessage, BotUpdateModel
from src.services.telegram_bot import TelegramBot
from src.conf.config import settings


telegram_bot = TelegramBot(settings.telegram_bot_token)

class AbstractHandler(ABC):
    """
    Abstract base class for handling requests in a chain of responsibility.

    Methods:
    - set_next(handler): Sets the next handler in the chain.
    - handle_request(request, db): Abstract method to handle a request.

    Attributes:
    - _next_handler: The next handler in the chain.
    """
    
    def set_next(self, handler):
        """
        Sets the next handler in the chain.

        Args:
        - handler: The next handler to be set in the chain.
        """ 
        self._next_handler = handler

    @abstractmethod
    def handle_request(self, request, db):
        """
        Abstract method to handle a request.

        Args:
        - request: The request object to be processed.
        - db: The database session or connection.

        Raises:
        - NotImplementedError: If the method is not implemented in a concrete subclass.
        """
        pass


class StartHandler(AbstractHandler):
    async def handle_request(self, request: BotUpdateModel):
        if request.message.text == '/start':
            return await telegram_bot.send_start_message(request)
        elif hasattr(self, "_next_handler"):
            await self._next_handler.handle_request(request)

class GetGymInfoHandler(AbstractHandler):
    async def handle_request(self, request: BotUpdateModel):
        if request.message.text:
            print("Processing gym info request")
            return await telegram_bot.send_csv_from_data(request)
        elif hasattr(self, "_next_handler"):
            await self._next_handler.handle_request(request)

class NoMessageHandler(AbstractHandler):
    async def handle_request(self, request: BotUpdateModel):
        if "," not in request.message.text or not request.message.text:
            return await telegram_bot.send_failure_message(request)
        elif hasattr(self, "_next_handler"):
            await self._next_handler.handle_request(request)

async def bot_request_handler_chain():

    start_handler = StartHandler()
    get_gym_info_handler = GetGymInfoHandler()
    no_message_handler = NoMessageHandler()

    start_handler.set_next(get_gym_info_handler)
    get_gym_info_handler.set_next(no_message_handler)
    no_message_handler.set_next(start_handler) 

    return start_handler



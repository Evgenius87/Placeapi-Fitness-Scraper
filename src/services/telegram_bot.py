
from aiohttp import ClientSession
from io import BytesIO
import aiohttp
import asyncio

from src.conf.bot_messages import START_MESSAGE, FAIL_MESSAGE, GYMS_LEN_MESSAGE, WARNING_MESSAGE
from src.schemas import BotUpdateModel
from src.services.google_map_service import get_gym_info
from src.services.split_message import slpit_message
from src.services.gyms_to_csv import gyms_to_csv



class TelegramBot:

    start_message = START_MESSAGE
    fail_message = FAIL_MESSAGE
    warning_message = WARNING_MESSAGE

    def __init__(self, API_key: str) -> None:
        self.TG_API = API_key
        self.SEND_MESSAGE_URL = f"https://api.telegram.org/bot{API_key}/sendMessage"
        self.SEND_DOCUMENT_URL = f"https://api.telegram.org/bot{self.TG_API}/sendDocument"


    async def send_message(self, chat_id: int, message: str):
        data = {
            'chat_id': chat_id,
            'text': message
        }
        async with ClientSession() as session:
            async with session.post(self.SEND_MESSAGE_URL, data=data) as response:
                result = {'message': 'ok'}
        return result


    async def send_start_message(self, request: BotUpdateModel):
        return await self.send_message(
            chat_id=request.message.from_tg.chat_id,
            message=self.start_message
        )
    
    async def send_failure_message(self, request: BotUpdateModel):
        return await self.send_message(
            chat_id=request.message.from_tg.chat_id,
            message=self.fail_message
        )
    
    async def send_warning_message(self, request: BotUpdateModel):
        return await self.send_message(
            chat_id=request.message.from_tg.chat_id,
            message=self.warning_message
        )
    
    async def send_processing_message(self, request: BotUpdateModel):
        """Відправляє повідомлення про початок обробки"""
        return await self.send_message(
            chat_id=request.message.from_tg.chat_id,
            message=self.processing_message
        )

    async def start_csv_processing(self, request: BotUpdateModel):
        await self.send_warning_message(request)
        asyncio.create_task(self.send_csv_from_data(request)) 
        return {"message": "processing started"}
        
        
    
    async def send_csv_from_data(self, request: BotUpdateModel, filename: str = "data.csv", caption: str = None):
        chat_id = request.message.from_tg.chat_id
        message = request.message.text
        city, country = slpit_message(message)
        if not city or not country:
            await self.send_failure_message(request)
            return {"error": "Invalid input format"}

        try:
            gyms = await get_gym_info(city, country)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            await self.send_message(
                chat_id=chat_id,
                message=f"⚠️ Failed to fetch gym info for *{city}, {country}*.\n\nError: `{str(e)}`"
            )
            return {"error": f"Exception occurred in get_gym_info: {str(e)}", "trace": tb}
        
        gyms_len = len(gyms)
        await self.send_message(
            chat_id=chat_id,
            message=GYMS_LEN_MESSAGE.format(gyms_len=gyms_len)
            )
        csv_data = gyms_to_csv(gyms)

        try:
            async with ClientSession() as session:
                data = aiohttp.FormData()
                data.add_field('chat_id', str(chat_id))

                csv_bytes = BytesIO(csv_data.encode('utf-8'))
                data.add_field(
                    'document',
                    csv_bytes,
                    filename=filename,
                    content_type='text/csv'
                )

                if caption:
                    data.add_field('caption', caption)

                async with session.post(self.SEND_DOCUMENT_URL, data=data) as response:
                    if response.status == 200:
                        result = {'message': 'CSV file sent successfully'}
                    else:
                        response_text = await response.text()
                        result = {'error': f'Failed to send file: {response_text}'}

        except Exception as e:
            import traceback
            result = {'error': f'Exception occurred: {str(e)}'}

        return result

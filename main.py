import uvicorn

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from src.schemas import BotUpdateModel
from src.bot_request_handler import bot_request_handler_chain
from pyngrok import ngrok



app = FastAPI()
origins = [
            "http://localhost:8000",  
           ] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get('/', status_code=status.HTTP_200_OK)
async def hello():
    message = {'message': 'hello!'}
    return message


@app.post('/webhook', status_code=status.HTTP_200_OK)
async def webhook_handler(obj: BotUpdateModel):
    bot_handler_chain = await bot_request_handler_chain()
    response = await bot_handler_chain.handle_request(obj)
    return {'message': 'ok'}




if __name__ == "__main__":
    
    PORT = 8000
    http_tunnel = ngrok.connect(PORT, bind_tls=True)
    HOST_URL = http_tunnel.public_url
    print("Ngrok public url:", HOST_URL)

    uvicorn.run("main:app", host="127.0.0.1", port=PORT, log_level="info", reload=True)
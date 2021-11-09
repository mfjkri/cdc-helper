import requests
from utils.common import utils
from utils.log import Log

class TelegramBot:
    def __init__(self, token:str, default_chat_id:int, log:Log):
        self.token = token
        self.default_chat_id = default_chat_id
        self.log = log
        
    def send_message(self, text:str, chat_id:int=None):
        chat_id = chat_id or self.default_chat_id
        return requests.get(f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}")
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import json
class SenexyBot:
def init(self):
with open("credentials.json") as f:
self.token = json.load(f).get("bot_token", "TOKEN")
self.bot = Bot(token=self.token)
self.dp = Dispatcher()
self.dp.message(Command("ping"))(self.ping)
async def ping(self, m: Message):
    await m.answer("🐧 Pong!")

async def start(self):
    await self.dp.start_polling(self.bot)
async def main():
await SenexyBot().start()
if name == "main":
asyncio.run(main())

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import json
import logging
from pathlib import Path
import asyncio
from bot_creator import create_inline_bot, enable_inline

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

PREFIXES = [".", "senexy", "snx", "hikka", "heroku", "ftg"]

class SenexyUserbot:
    def __init__(self):
        logger.info("🐧 Senexy Userbot v1.0")
        
        if not Path("credentials.json").exists():
            logger.error("❌ Not configured! Run: python senexy.py")
            exit(1)
        
        creds = json.load(open("credentials.json"))
        
        self.app = Client(
            "senexy_session",
            api_id=int(creds["api_id"]),
            api_hash=creds["api_hash"]
        )
        
        self.start_time = datetime.now()
        self.cmd_count = 0
        self.modules = ["core"]
        self.log_group_id = None
        self.bot_token = creds.get("bot_token")
        self.inline_bot = None
        
        self.setup_handlers()
    
    async def setup_inline_bot(self):
        if not self.bot_token:
            logger.info("🤖 No inline bot found, creating...")
            self.bot_token = await create_inline_bot(self.app)
            
            if self.bot_token:
                creds = json.load(open("credentials.json"))
                creds["bot_token"] = self.bot_token
                
                with open("credentials.json", "w") as f:
                    json.dump(creds, f, indent=2)
                
                me = await self.app.get_me()
                bot_username = f"senexy_{me.id}_bot"
                await enable_inline(self.app, bot_username)
                
                creds["bot_username"] = bot_username
                with open("credentials.json", "w") as f:
                    json.dump(creds, f, indent=2)
        
        if self.bot_token:
            from pyrogram import Client as BotClient
            self.inline_bot = BotClient(
                "inline_bot",
                api_id=int(json.load(open("credentials.json"))["api_id"]),
                api_hash=json.load(open("credentials.json"))["api_hash"],
                bot_token=self.bot_token
            )
            await self.inline_bot.start()
            logger.info("✅ Inline bot connected")
    
    async def create_log_group(self):
        logger.info("📁 Creating log group...")
        
        async for dialog in self.app.get_dialogs():
            if dialog.chat.title and "Senexy Logs" in dialog.chat.title:
                self.log_group_id = dialog.chat.id
                logger.info(f"✅ Found log group: {dialog.chat.id}")
                return
        
        try:
            me = await self.app.get_me()
            group = await self.app.create_group("Senexy Logs 🐧", [me.id])
            self.log_group_id = group.id
            
            await self.app.send_message(
                group.id,
                "**🐧 Senexy Logs**\n\nLogs and backups storage"
            )
            
            logger.info(f"✅ Created log group: {group.id}")
        except Exception as e:
            logger.error(f"❌ Failed: {e}")
    
    async def send_log(self, text):
        if self.log_group_id:
            try:
                await self.app.send_message(self.log_group_id, text)
            except:
                pass
    
    def setup_handlers(self):
        @self.app.on_message(filters.me & filters.command("ping", prefixes=PREFIXES))
        async def ping(c, m: Message):
            self.cmd_count += 1
            start = datetime.now()
            msg = await m.edit("🐧")
            ms = (datetime.now() - start).microseconds / 1000
            await msg.edit(f"**Senexy**\n⚡️ `{ms}ms`")
            await self.send_log(f"📡 Ping: {ms}ms")
        
        @self.app.on_message(filters.me & filters.command("help", prefixes=PREFIXES))
        async def help_cmd(c, m: Message):
            self.cmd_count += 1
            
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📦 Modules", callback_data="modules")],
                [InlineKeyboardButton("ℹ️ Info", callback_data="info")],
                [InlineKeyboardButton("❌ Close", callback_data="close")]
            ])
            
            await m.edit(
                f"**🐧 Senexy Userbot**\n\n"
                f"**Modules:** `{len(self.modules)}`\n"
                f"**Prefixes:** `{', '.join(PREFIXES)}`\n\n"
                f"**Commands:**\n"
                f"`.ping` - Speed test\n"
                f"`.alive` - Bot info\n"
                f"`.help` - This menu\n"
                f"`.modules` - Module list",
                reply_markup=keyboard
            )
        
        @self.app.on_message(filters.me & filters.command("alive", prefixes=PREFIXES))
        async def alive(c, m: Message):
            self.cmd_count += 1
            uptime = datetime.now() - self.start_time
            h = int(uptime.total_seconds() // 3600)
            mins = int((uptime.total_seconds() % 3600) // 60)
            
            me = await c.get_me()
            
            await m.edit(
                f"**🐧 Senexy Userbot**\n\n"
                f"**User:** {me.first_name}\n"
                f"**ID:** `{me.id}`\n"
                f"**Username:** @{me.username or 'None'}\n\n"
                f"**Uptime:** `{h}h {mins}m`\n"
                f"**Commands:** `{self.cmd_count}`\n"
                f"**Modules:** `{len(self.modules)}`\n\n"
                f"**Status:** ✅ Active"
            )
        
        @self.app.on_message(filters.me & filters.command("modules", prefixes=PREFIXES))
        async def modules_cmd(c, m: Message):
            self.cmd_count += 1
            mods = "\n".join([f"{i}. `{mod}`" for i, mod in enumerate(self.modules, 1)])
            await m.edit(
                f"**🐧 Loaded Modules ({len(self.modules)})**\n\n{mods}"
            )
    
    async def startup(self):
        await self.create_log_group()
        await self.setup_inline_bot()
        
        me = await self.app.get_me()
        
        startup_msg = (
            f"🐧 **Senexy Started**\n\n"
            f"👤 {me.first_name}\n"
            f"🆔 `{me.id}`\n"
            f"🤖 Bot: {'✅' if self.bot_token else '❌'}\n"
            f"⏰ {datetime.now().strftime('%H:%M:%S')}"
        )
        
        await self.send_log(startup_msg)
        logger.info(f"✅ Started as: {me.first_name}")
    
    def run(self):
        logger.info("="*50)
        logger.info("🚀 Starting...")
        logger.info("="*50 + "\n")
        
        @self.app.on_message(filters.me)
        async def init(c, m):
            await self.startup()
            self.app.remove_handler(init)
        
        try:
            self.app.run()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopped")
            if self.inline_bot:
                self.inline_bot.stop()

if __name__ == "__main__":
    SenexyUserbot().run()

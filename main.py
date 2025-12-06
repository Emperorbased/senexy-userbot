from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
import json
import logging
from pathlib import Path

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
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.app.on_message(filters.me & filters.command("ping", prefixes=PREFIXES))
        async def ping(c, m: Message):
            self.cmd_count += 1
            start = datetime.now()
            msg = await m.edit("🐧")
            ms = (datetime.now() - start).microseconds / 1000
            await msg.edit(f"**Senexy Userbot**\n⚡️ `{ms}ms`")
        
        @self.app.on_message(filters.me & filters.command("help", prefixes=PREFIXES))
        async def help_cmd(c, m: Message):
            self.cmd_count += 1
            mods = "\n".join([f"• `{mod}`" for mod in self.modules])
            await m.edit(
                f"**🐧 Senexy Modules**\n\n"
                f"{mods}\n\n"
                f"**Prefixes:**\n`{', '.join(PREFIXES)}`\n\n"
                f"**Commands:**\n"
                f"`.ping` - Speed test\n"
                f"`.alive` - Bot info\n"
                f"`.help` - This message"
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
            mods_list = "\n".join([f"{i}. `{mod}`" for i, mod in enumerate(self.modules, 1)])
            await m.edit(
                f"**🐧 Loaded Modules ({len(self.modules)})**\n\n"
                f"{mods_list}"
            )
    
    def run(self):
        logger.info("="*50)
        logger.info("🚀 Starting...")
        logger.info(f"📌 Prefixes: {', '.join(PREFIXES)}")
        logger.info("="*50 + "\n")
        
        try:
            self.app.run()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopped")

if __name__ == "__main__":
    SenexyUserbot().run()

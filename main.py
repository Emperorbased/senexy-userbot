from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import json
import logging
import psutil
import os
from pathlib import Path
import aiohttp
import importlib.util
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class SenexyUserbot:
    def __init__(self):
        logger.info("🐧 Senexy Userbot Beta")
        
        if not Path("credentials.json").exists():
            logger.error("❌ Not configured!")
            exit(1)
        
        self.config = self.load_config()
        creds = json.load(open("credentials.json"))
        
        self.app = Client(
            "senexy_session",
            api_id=int(creds["api_id"]),
            api_hash=creds["api_hash"]
        )
        
        self.start_time = datetime.now()
        self.cmd_count = 0
        self.prefix = self.config.get("prefix", ".")
        self.modules = {}
        self.version = "1.0.0-beta"
        self.branch = "dev"
        
        self.load_modules()
        self.setup_handlers()
    
    def load_config(self):
        config_path = Path("configs/config.json")
        if config_path.exists():
            return json.load(open(config_path))
        
        default = {
            "prefix": ".",
            "owner": "Anonymous",
            "modules": {}
        }
        
        Path("configs").mkdir(exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(default, f, indent=2)
        
        return default
    
    def save_config(self):
        with open("configs/config.json", "w") as f:
            json.dump(self.config, f, indent=2)
    
    def load_modules(self):
        modules_dir = Path("modules")
        if not modules_dir.exists():
            return
        
        for file in modules_dir.glob("*.py"):
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.modules[file.stem] = module
                logger.info(f"✅ Loaded: {file.stem}")
            except Exception as e:
                logger.error(f"❌ Failed {file.stem}: {e}")
    
    def get_size(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
    
    def setup_handlers(self):
        @self.app.on_message(filters.me & filters.command("ping", prefixes=self.prefix))
        async def ping(c, m: Message):
            self.cmd_count += 1
            start = datetime.now()
            msg = await m.edit("🐧")
            ms = (datetime.now() - start).microseconds / 1000
            await msg.edit(f"<b>Senexy</b>\n⚡️ <code>{ms}ms</code>")
        
        @self.app.on_message(filters.me & filters.command("alive", prefixes=self.prefix))
        async def alive(c, m: Message):
            self.cmd_count += 1
            
            uptime = datetime.now() - self.start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime_str = f"{days} day(s), {hours}:{minutes:02d}:{seconds:02d}"
            
            me = await c.get_me()
            owner_link = f"<a href='tg://user?id={me.id}'>{self.config.get('owner', me.first_name)}</a>"
            
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory()
            ram_used = self.get_size(ram.used)
            
            ping_start = datetime.now()
            await c.get_me()
            ping = (datetime.now() - ping_start).microseconds / 1000
            
            text = (
                f"<b>❤️ Senexy Userbot</b>\n\n"
                f"<blockquote>⭐️ Owner: {owner_link}\n"
                f"❗️ Version: {self.version}\n"
                f"🔗 Branch: {self.branch}</blockquote>\n\n"
                f"<blockquote>🔨 Prefix: «{self.prefix}»\n"
                f"🕓 Uptime: {uptime_str}\n"
                f"🎛 Ping: {ping:.3f}ms</blockquote>\n\n"
                f"<blockquote>💼 CPU Usage: ~{cpu}%\n"
                f"📊 RAM Usage: ~{ram_used}\n"
                f"💧 Host: 📱 Termux</blockquote>"
            )
            
            await m.edit(text)
        
        @self.app.on_message(filters.me & filters.command("setprefix", prefixes=self.prefix))
        async def setprefix(c, m: Message):
            args = m.text.split(maxsplit=1)
            if len(args) < 2:
                await m.edit(f"<b>Usage:</b> <code>{self.prefix}setprefix [new]</code>")
                return
            
            old = self.prefix
            self.prefix = args[1]
            self.config["prefix"] = self.prefix
            self.save_config()
            
            await m.edit(
                f"<b>✅ Prefix changed</b>\n\n"
                f"Old: <code>{old}</code>\n"
                f"New: <code>{self.prefix}</code>"
            )
        
        @self.app.on_message(filters.me & filters.command("dlm", prefixes=self.prefix))
        async def dlm(c, m: Message):
            args = m.text.split(maxsplit=1)
            if len(args) < 2:
                await m.edit(f"<b>Usage:</b> <code>{self.prefix}dlm [url]</code>")
                return
            
            url = args[1]
            status = await m.edit("🐧 Downloading module...")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            await status.edit(f"❌ HTTP {resp.status}")
                            return
                        
                        code = await resp.text()
                        filename = url.split('/')[-1]
                        
                        if not filename.endswith('.py'):
                            filename += '.py'
                        
                        Path("modules").mkdir(exist_ok=True)
                        module_path = Path("modules") / filename
                        
                        with open(module_path, 'w') as f:
                            f.write(code)
                        
                        try:
                            spec = importlib.util.spec_from_file_location(module_path.stem, module_path)
                            module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(module)
                            self.modules[module_path.stem] = module
                            
                            await status.edit(
                                f"<b>✅ Module installed</b>\n\n"
                                f"📦 Name: <code>{module_path.stem}</code>\n"
                                f"🔗 URL: <code>{url[:50]}...</code>\n\n"
                                f"💡 Restart to load: <code>{self.prefix}restart</code>"
                            )
                        except Exception as e:
                            await status.edit(f"<b>⚠️ Downloaded but not loaded</b>\n\n<code>{str(e)}</code>")
            
            except Exception as e:
                await status.edit(f"<b>❌ Error</b>\n\n<code>{str(e)}</code>")
        
        @self.app.on_message(filters.me & filters.command("modules", prefixes=self.prefix))
        async def modules_list(c, m: Message):
            if not self.modules:
                await m.edit("<b>📦 No modules loaded</b>")
                return
            
            mods = "\n".join([f"• <code>{name}</code>" for name in self.modules.keys()])
            await m.edit(
                f"<b>🐧 Senexy Modules ({len(self.modules)})</b>\n\n"
                f"{mods}"
            )
        
        @self.app.on_message(filters.me & filters.command("cfg", prefixes=self.prefix))
        async def cfg(c, m: Message):
            builtin = ["core"]
            custom = list(self.modules.keys())
            
            keyboard = [
                [InlineKeyboardButton("🔧 Built-in Modules", callback_data="cfg_builtin")],
                [InlineKeyboardButton("📦 Custom Modules", callback_data="cfg_custom")],
                [InlineKeyboardButton("⚙️ Settings", callback_data="cfg_settings")],
                [InlineKeyboardButton("❌ Close", callback_data="cfg_close")]
            ]
            
            await m.edit(
                f"<b>🐧 Senexy Config</b>\n\n"
                f"<b>Built-in:</b> <code>{len(builtin)}</code>\n"
                f"<b>Custom:</b> <code>{len(custom)}</code>\n\n"
                f"Select category:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        @self.app.on_message(filters.me & filters.command("help", prefixes=self.prefix))
        async def help_cmd(c, m: Message):
            await m.edit(
                f"<b>🐧 Senexy Commands</b>\n\n"
                f"<b>Core:</b>\n"
                f"<code>{self.prefix}ping</code> - Speed test\n"
                f"<code>{self.prefix}alive</code> - Bot info\n"
                f"<code>{self.prefix}help</code> - This message\n\n"
                f"<b>Modules:</b>\n"
                f"<code>{self.prefix}modules</code> - List modules\n"
                f"<code>{self.prefix}dlm [url]</code> - Download module\n"
                f"<code>{self.prefix}cfg</code> - Configure\n\n"
                f"<b>Settings:</b>\n"
                f"<code>{self.prefix}setprefix [new]</code> - Change prefix"
            )
        
        @self.app.on_message(filters.me & filters.command("restart", prefixes=self.prefix))
        async def restart(c, m: Message):
            await m.edit("<b>🔄 Restarting...</b>")
            os.execl(sys.executable, sys.executable, "main.py")
    
    async def startup(self):
        me = await self.app.get_me()
        
        try:
            await self.app.send_message(
                "me",
                f"<b>🐧 Senexy Beta Bot</b>\n\n"
                f"Welcome to Senexy Userbot!\n\n"
                f"<b>Version:</b> <code>{self.version}</code>\n"
                f"<b>Branch:</b> <code>{self.branch}</code>\n"
                f"<b>Prefix:</b> <code>{self.prefix}</code>\n\n"
                f"Type <code>{self.prefix}help</code> for commands"
            )
        except:
            pass
        
        logger.info(f"✅ Started as: {me.first_name}")
        logger.info(f"🔨 Prefix: {self.prefix}")
        logger.info(f"📦 Modules: {len(self.modules)}")
    
    def run(self):
        logger.info("="*50)
        logger.info("🚀 Senexy Userbot Beta")
        logger.info(f"📌 Version: {self.version}")
        logger.info(f"🔗 Branch: {self.branch}")
        logger.info("="*50 + "\n")
        
        @self.app.on_message(filters.me)
        async def init(c, m):
            await self.startup()
            self.app.remove_handler(init)
        
        try:
            self.app.run()
        except KeyboardInterrupt:
            logger.info("\n🛑 Stopped")

if __name__ == "__main__":
    SenexyUserbot().run()

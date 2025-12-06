from pyrogram import Client
from pyrogram.types import Message
import asyncio
import json
import re

async def create_inline_bot(app: Client):
    print("\n🤖 Creating inline bot via @BotFather...")
    
    try:
        await app.send_message("@BotFather", "/newbot")
        await asyncio.sleep(2)
        
        me = await app.get_me()
        bot_name = f"{me.first_name} Inline"
        await app.send_message("@BotFather", bot_name)
        await asyncio.sleep(2)
        
        bot_username = f"senexy_{me.id}_bot"
        await app.send_message("@BotFather", bot_username)
        await asyncio.sleep(3)
        
        async for message in app.get_chat_history("@BotFather", limit=1):
            if "token" in message.text.lower():
                token_match = re.search(r'(\d+:[A-Za-z0-9_-]+)', message.text)
                if token_match:
                    bot_token = token_match.group(1)
                    print(f"✅ Bot created: @{bot_username}")
                    print(f"🔑 Token: {bot_token[:20]}...")
                    return bot_token
            elif "already taken" in message.text.lower():
                print(f"⚠️  @{bot_username} already exists")
                
                await app.send_message("@BotFather", "/mybots")
                await asyncio.sleep(2)
                
                return None
        
        print("❌ Failed to get token")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def enable_inline(app: Client, bot_username: str):
    print("\n⚙️ Enabling inline mode...")
    
    try:
        await app.send_message("@BotFather", "/setinline")
        await asyncio.sleep(2)
        
        await app.send_message("@BotFather", f"@{bot_username}")
        await asyncio.sleep(2)
        
        await app.send_message("@BotFather", "Search...")
        await asyncio.sleep(2)
        
        print("✅ Inline mode enabled")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

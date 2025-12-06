import asyncio
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded, PhoneCodeInvalid
import json
from pathlib import Path
import os

LOGO = """
╔═══════════════════════════════════════╗
║     🐧 SENEXY USERBOT SETUP 🐧       ║
╚═══════════════════════════════════════╝
"""

async def terminal_login():
    print(LOGO)
    print("🔐 Terminal Authorization\n")
    
    Path("configs").mkdir(exist_ok=True)
    
    api_id = input("📱 API ID: ")
    api_hash = input("🔑 API Hash: ")
    phone = input("📞 Phone (+): ")
    
    app = Client("senexy_session", api_id=int(api_id), api_hash=api_hash)
    
    await app.connect()
    
    print("\n📤 Sending code...")
    sent_code = await app.send_code(phone)
    
    code = input("📨 Code: ")
    
    try:
        await app.sign_in(phone, sent_code.phone_code_hash, code)
        print("\n✅ Logged in!")
    except SessionPasswordNeeded:
        password = input("🔐 2FA Password: ")
        await app.check_password(password)
        print("\n✅ Logged in!")
    except PhoneCodeInvalid:
        print("\n❌ Invalid code!")
        await app.disconnect()
        return
    
    me = await app.get_me()
    
    creds = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "user_id": me.id,
        "username": me.username or "None",
        "first_name": me.first_name,
        "prefix": "."
    }
    
    with open("credentials.json", "w") as f:
        json.dump(creds, f, indent=2)
    
    print(f"\n🐧 Welcome, {me.first_name}!")
    print(f"🆔 ID: {me.id}")
    print(f"📝 @{me.username or 'No username'}")
    print("\n✅ Setup complete!")
    print("🚀 Run: python main.py")
    
    await app.disconnect()

def web_login():
    import secrets
    session_id = secrets.token_urlsafe(16)
    print(LOGO)
    print("🌐 Web Authorization\n")
    print(f"Open: http://localhost:5000?session={session_id}\n")
    os.system(f"python web_setup.py {session_id}")

def main():
    print(LOGO)
    print("Choose setup method:\n")
    print("1. Terminal (fastest)")
    print("2. Web Interface\n")
    
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(terminal_login())
    elif choice == "2":
        web_login()
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()

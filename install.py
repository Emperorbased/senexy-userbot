import os
import sys
import secrets
from pathlib import Path
print("🐧 Senexy Installation")
print("="*40)
Path("templates").mkdir(exist_ok=True)
Path("configs").mkdir(exist_ok=True)
Path("modules").mkdir(exist_ok=True)
session_id = secrets.token_urlsafe(16)
print(f"\n🌐 Open: http://localhost:5000?session={session_id}\n")
os.system(f"python web_setup.py {session_id}")

#!/bin/bash
sudo apt update
sudo apt install -y python3 python3-pip git
git clone https://github.com/Emperorbased/senexy-userbot.git
cd senexy-userbot
pip3 install -r requirements.txt
echo "Done! Run: python3 install.py"

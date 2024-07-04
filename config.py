import os

API_ID = int(os.environ.get("API_ID",""))
API_HASH = os.environ.get("API_HASH","")
BOT_TOKEN = os.environ.get("BOT_TOKEN","")
CHANNELS = [int(channel_id) for channel_id in os.environ.get("CHANNELS", "").split()]
OWNER_ID = int(os.environ.get("OWNER_ID",1280356202))
PAYMENT_CHANNEL = int(os.environ.get("PAYMENT_CHANNEL",""))
DAILY_BONUS = int(os.environ.get("DAILY_BONUS", 1))
MINI_WITHDRAW = int(os.environ.get("MINI_WITHDRAW", 2))
PER_REFER = int(os.environ.get("PER_REFER", 100))

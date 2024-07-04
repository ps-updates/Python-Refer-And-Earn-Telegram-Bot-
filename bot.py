from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import json
import time
from config import API_ID, API_HASH, BOT_TOKEN, CHANNELS, OWNER_ID, PAYMENT_CHANNEL, DAILY_BONUS, MINI_WITHDRAW, PER_REFER

app = Client("new bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN
            )
            
# Load or initialize user data
def load_or_init_user_data():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"referred": {}, "total": 0, "totalwith": 0}

# Save user data
def save_user_data(data):
    with open('users.json', 'w') as file:
        json.dump(data, file, indent=4)
        
        
# Fetch channel invite link dynamically
async def get_channel_invite_link(client, channel_id):
    try:
        chat = await client.get_chat(channel_id)
        if chat.invite_link:
            return chat.invite_link
        else:
            # Attempt to create a new invite link if possible
            return await client.export_chat_invite_link(channel_id)
    except Exception as e:
        print(f"Error fetching invite link for channel {channel_id}: {e}")
        return None
        
# Check user membership in all required channels
async def check_membership(client, user_id):
    for channel in CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status == "left":
                return False
        except Exception as e:
            print(f"Failed to check membership for {user_id} in {channel}: {e}")
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = str(message.chat.id)
    args = message.command
    user_data = load_or_init_user_data()
    if len(args) > 1:  # handle referral links /start ref_user_id
        referrer_id = args[1]
    else:
        referrer_id = user_id

    if user_id not in user_data:
        user_data['referred'][user_id] = 0
        user_data['referby'][user_id] = referrer_id
        user_data['total'] += 1
        user_data[user_id] = {"checkin": 0, "balance": 0, "wallet": "none", "withd": 0, "id": user_data['total']}

    save_user_data(user_data)

    # Check membership
    # Check membership
    if await check_membership(client, user_id):
        await menu(client, message, user_id)
    else:
        link = await get_channel_invite_link(client, CHANNELS[0])
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=link)]])
        await message.reply("You must join the channel to use this bot.", reply_markup=keyboard)

"""@app.on_message(filters.text & ~filters.command)
async def handle_text(client, message: Message):
    # This can handle various text inputs like setting wallet, responding to queries, etc.
    pass"""

async def menu(client, message, user_id):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🆔 Account", callback_data="account"),
         InlineKeyboardButton("🙌🏻 Referrals", callback_data="referrals"),
         InlineKeyboardButton("🎁 Bonus", callback_data="bonus")],
        [InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
         InlineKeyboardButton("⚙️ Set Wallet", callback_data="set_wallet"),
         InlineKeyboardButton("📊Statistics", callback_data="stats")]
    ])
    await message.reply("Welcome to the bot!", reply_markup=keyboard)

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    user_id = str(callback_query.from_user.id)

    if data == "account":
        user_data = load_or_init_user_data()
        account_info = f"👤 Account Info:\n\n💰 Balance: {user_data.get(user_id, {}).get('balance', 0)} {TOKEN}\n🎫 ID: {user_data.get(user_id, {}).get('id', 'Not set')}"
        await callback_query.message.edit_text(account_info)
    elif data.startswith("withdraw"):
        await handle_withdraw(client, callback_query)
    # Add other elif blocks for different callback data handling like "referrals", "bonus", etc.

async def handle_withdraw(client, callback_query):
    user_id = str(callback_query.from_user.id)
    user_data = load_or_init_user_data()
    balance = user_data.get(user_id, {}).get('balance', 0)
    if balance >= MINI_WITHDRAW:
        # Process withdrawal here
        await callback_query.answer("Processing withdrawal...", show_alert=True)
    else:
        await callback_query.answer(f"Minimum withdrawal amount is {MINI_WITHDRAW}.", show_alert=True)

if __name__ == "__main__":
    app.run()

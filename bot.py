from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import json
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
        return {"referred": {}, "total": 0}

# Save user data
def save_user_data(data):
    with open('users.json', 'w') as file:
        json.dump(data, file, indent=4)

# Check user membership in all required channels
async def check_membership(client, user_id):
    for channel in CHANNELS:
        try:
            member = await client.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except Exception as e:
            print(f"Failed to check membership for {user_id} in {channel}: {e}")
            return False
    return True

@app.on_message(filters.command("start"))
async def start(client, message: Message):
    user_id = str(message.from_user.id)
    user_data = load_or_init_user_data()

    # Initialize user data if new user
    if user_id not in user_data['referred']:
        user_data['referred'][user_id] = 0
        user_data['total'] += 1
        user_data[user_id] = {"checkin": 0, "balance": 0, "wallet": "none"}

    save_user_data(user_data)

    # Send welcome message with keyboard
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📔 Account", callback_data="account")],
        [InlineKeyboardButton("🙌 Referrals", callback_data="referrals"),
         InlineKeyboardButton("🎉 Bonus", callback_data="bonus"),
         InlineKeyboardButton("💸 Withdraw", callback_data="withdraw")]
    ])
    await message.reply("Welcome to the bot!", reply_markup=keyboard)

@app.on_callback_query(filters.regex("^withdraw$"))
async def handle_withdraw(client, callback_query):
    user_id = str(callback_query.from_user.id)
    user_data = load_or_init_user_data()

    if int(user_data[user_id]['balance']) < MINI_WITHDRAW:
        await callback_query.answer("Minimum withdrawal amount is not met.", show_alert=True)
        return

    # Process the withdrawal here (e.g., send a notification to admin)
    # Assuming processing function 'process_withdrawal' exists
    await process_withdrawal(client, user_id, user_data, PAYMENT_CHANNEL)

async def process_withdrawal(client, user_id, user_data, payment_channel):
    amount = user_data[user_id]['balance']
    user_data['total'] -= amount
    user_data[user_id]['balance'] = 0
    save_user_data(user_data)

    # Notify payment channel
    message_text = f"New Withdraw Request: User {user_id}, Amount: {amount}"
    await client.send_message(payment_channel, message_text)

    # Confirm to user
    await client.send_message(user_id, "Your withdrawal request has been processed.")

if __name__ == "__main__":
    app.run()

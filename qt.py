import os
import asyncio
import threading
import logging
import requests
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.utils import get_display_name
from flask import Flask
from pymongo import MongoClient
# ConnectionError အစား ServerSelectionTimeoutError ကို သုံးလိုက်သည်
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError 

# ==============================================================================
# 1. Configuration & Setup
# ==============================================================================

# Logging Configuration
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# --- Hardcoded Credentials (Replace with your actual data!) ---
# ⚠️ REPLACE THESE WITH YOUR REAL VALUES!
API_ID = 21308016     # <-- ဤနေရာတွင် သင့် API ID အမှန်ကို ထည့်ပါ
API_HASH = "9a483e059bcb0904e9f367418076091e"    # <-- ဤနေရာတွင် သင့် API HASH အမှန်ကို ထည့်ပါ
# OWNER ID တစ်ခုတည်းကိုသာ ထားရှိရပါမည် (Integer)
OWNER_ID = 7781882070    # <-- ဤနေရာတွင် သင့် OWNER ID အမှန်ကို ထည့်ပါ 
MONGO_URI = "mongodb+srv://sailinthitaung_db_user:ZBEIl2SKHMFr8RPw@accbot.lidtexj.mongodb.net/?retryWrites=true&w=majority&appName=accbot"

# --- Environment Variable Fallbacks (for Render URL/Session) ---
SESSION_STRING = os.environ.get("BOT_SESSION", None)
RENDER_URL = os.environ.get("RENDER_URL", "http://localhost:5000")

# --- Database Setup (MongoDB) ---
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.server_info()
    db = mongo_client["UserBotDB"]
    
    # Collections for persistence
    reply_collection = db["auto_replies"]
    data_collection = db["bot_data"]
    admin_collection = db["admin_users"] 
    
    logging.warning("✅ MongoDB Connection Successful.")
# ConnectionError အစား ServerSelectionTimeoutError ကို သုံးသည်
except ServerSelectionTimeoutError: 
    logging.error("❌ MongoDB Connection Failed. Check MONGO_URI and network access.")
    exit(1)
except Exception as e:
    logging.error(f"❌ MongoDB initialization error: {e}")
    exit(1)

# --- Global Data Storage (In-memory cache for quick access) ---
AUTO_REPLIES = {}  
AUTO_DELETE_USERS = {}  
AUTO_MENTION_USERS = {}  
EXISTING_REPLY_TARGETS = {}  
ADMIN_IDS = set() 
MENTION_INTERVAL = 300
IS_BOT_RUNNING = True

# --- Telethon Client Setup ---
if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("userbot_session", API_ID, API_HASH)

# ==============================================================================
# 2. Database (Persistence) Functions
# ==============================================================================

def load_data_from_db():
    """Loads all data (Replies, Admin list, and other config) from MongoDB."""
    global AUTO_REPLIES, AUTO_DELETE_USERS, AUTO_MENTION_USERS, EXISTING_REPLY_TARGETS, MENTION_INTERVAL, IS_BOT_RUNNING, ADMIN_IDS
    
    # Load Admin IDs 
    try:
        admin_data = admin_collection.find()
        # Ensure IDs are integers for proper comparison
        ADMIN_IDS = {doc['user_id'] for doc in admin_data}
        logging.warning(f"👑 Loaded {len(ADMIN_IDS)} admin IDs.")
    except Exception as e:
        logging.error(f"Failed to load ADMIN_IDS: {e}")

    # Load Auto Replies
    try:
        data = reply_collection.find()
        AUTO_REPLIES = {doc['trigger']: doc['reply'] for doc in data}
        logging.warning(f"🤖 Loaded {len(AUTO_REPLIES)} auto-replies.")
    except Exception as e:
        logging.error(f"Failed to load AUTO_REPLIES: {e}")

    # Load Global Bot Data (Mentions, Deletes, etc.)
    try:
        bot_data_doc = data_collection.find_one({'_id': 'global_data'})
        if bot_data_doc:
            AUTO_DELETE_USERS = bot_data_doc.get('auto_delete_users', {})
            AUTO_MENTION_USERS = bot_data_doc.get('auto_mention_users', {})
            EXISTING_REPLY_TARGETS = bot_data_doc.get('existing_reply_targets', {})
            MENTION_INTERVAL = bot_data_doc.get('mention_interval', 300)
            IS_BOT_RUNNING = bot_data_doc.get('is_bot_running', True)
            logging.warning("⚙️ Loaded global bot configurations.")
    except Exception as e:
        logging.error(f"Failed to load global bot data: {e}")


def save_global_data_to_db():
    """Saves all current global data to MongoDB."""
    global AUTO_DELETE_USERS, AUTO_MENTION_USERS, EXISTING_REPLY_TARGETS, MENTION_INTERVAL, IS_BOT_RUNNING
    try:
        data_collection.update_one(
            {'_id': 'global_data'},
            {'$set': {
                'auto_delete_users': AUTO_DELETE_USERS,
                'auto_mention_users': AUTO_MENTION_USERS,
                'existing_reply_targets': EXISTING_REPLY_TARGETS,
                'mention_interval': MENTION_INTERVAL,
                'is_bot_running': IS_BOT_RUNNING
            }},
            upsert=True
        )
        logging.info("💾 Global bot configurations saved.")
    except OperationFailure as e:
        logging.error(f"Failed to save global bot data: {e}")


def save_reply_to_db(trigger, reply):
    """Adds a new auto-reply to MongoDB."""
    try:
        reply_collection.update_one(
            {'trigger': trigger},
            {'$set': {'reply': reply}},
            upsert=True
        )
        AUTO_REPLIES[trigger] = reply
        return True
    except OperationFailure:
        return False

def remove_reply_from_db(trigger):
    """Removes an auto-reply from MongoDB."""
    try:
        result = reply_collection.delete_one({'trigger': trigger})
        if result.deleted_count > 0:
            if trigger in AUTO_REPLIES:
                del AUTO_REPLIES[trigger]
            return True
        return False
    except OperationFailure:
        return False

# ==============================================================================
# 3. Command Menu Helper
# ==============================================================================

COMMAND_MENU = """
🚀 **Userbot Command Menu** 🚀

**OWNER CONTROL (Owner Only):**
• `/stopbot` - Bot ၏ လုပ်ဆောင်မှုများ ရပ်ဆိုင်းရန်။
• `/startbot` - Bot လုပ်ဆောင်မှုများ ပြန်လည်စတင်ရန်။
• `/add_admin <id>` - ID ဖြင့် Admin ထည့်ရန်။
• `/remove_admin <id>` - ID ဖြင့် Admin ဖယ်ရန်။

**ADMIN/OWNER ONLY:**
• `/getid` - (Common)
• `/help` - (Common)
• `\.addreply [trigger] \| [reply]` - Auto-Reply အသစ် ထည့်/ပြင်ရန်။
• `\.delreply [trigger]` - Auto-Reply ဖျက်ရန်။
• `\.listreplies` - Auto-Reply စာရင်းကြည့်ရန်။
• **AUTO-DELETE** commands.
• **AUTO-MENTION** commands.

**COMMON (Everyone):**
• `/getid` - သင့်ရဲ့ User ID နှင့် Chat ID ကို ရယူရန်။
• `/help` - ဤ Menu ကို ပြသရန်။
"""

# ==============================================================================
# 4. Telethon Event Handlers (Commands)
# ==============================================================================

def is_owner(event):
    """Check if the sender is the OWNER_ID."""
    return event.sender_id == OWNER_ID

def is_admin_or_owner(event):
    """Check if the sender is the OWNER_ID or an ADMIN_ID."""
    return event.sender_id == OWNER_ID or event.sender_id in ADMIN_IDS

# --- OWNER ONLY: Admin Management ---

@client.on(events.NewMessage(pattern=r'(\.add_admin|\/add_admin) (\d+)', outgoing=True))
async def add_admin_handler(event):
    if not is_owner(event): return
    
    try:
        new_admin_id = int(event.pattern_match.group(2))
        
        if new_admin_id == OWNER_ID:
            await event.edit("❌ Owner ကို ထပ်ပြီး Admin ထည့်စရာ မလိုပါဘူး။")
            return

        if new_admin_id in ADMIN_IDS:
            await event.edit(f"💡 User ID `{new_admin_id}` သည် Admin စာရင်းတွင် ရှိပြီးသား ဖြစ်ပါသည်။")
            return
            
        # Add to DB
        admin_collection.update_one(
            {'user_id': new_admin_id},
            {'$set': {'user_id': new_admin_id}},
            upsert=True
        )
        # Add to memory
        ADMIN_IDS.add(new_admin_id)
        
        await event.edit(f"✅ User ID `{new_admin_id}` ကို Admin စာရင်းသို့ ထည့်သွင်းလိုက်ပါသည်။")
    except Exception as e:
        logging.error(f"Add admin error: {e}")
        await event.edit("❌ Error! Invalid format or database error. Use: `/add_admin <user_id>`")

@client.on(events.NewMessage(pattern=r'(\.remove_admin|\/remove_admin) (\d+)', outgoing=True))
async def remove_admin_handler(event):
    if not is_owner(event): return
    
    try:
        admin_to_remove = int(event.pattern_match.group(2))

        if admin_to_remove == OWNER_ID:
            await event.edit("❌ Owner ID ကို Admin စာရင်းမှ ဖယ်ရှားခွင့် မရှိပါ။")
            return

        if admin_to_remove not in ADMIN_IDS:
            await event.edit(f"💡 User ID `{admin_to_remove}` သည် Admin စာရင်းတွင် မရှိပါ။")
            return
            
        # Remove from DB
        admin_collection.delete_one({'user_id': admin_to_remove})
        # Remove from memory
        ADMIN_IDS.remove(admin_to_remove)
        
        await event.edit(f"✅ User ID `{admin_to_remove}` ကို Admin စာရင်းမှ ဖယ်ရှားလိုက်ပါသည်။")
    except Exception as e:
        logging.error(f"Remove admin error: {e}")
        await event.edit("❌ Error! Invalid format or database error. Use: `/remove_admin <user_id>`")

# --- COMMON Commands (Everyone/Admin) ---

@client.on(events.NewMessage(pattern=r'\.help|\/help', outgoing=True)) # outgoing=True ထည့်ထားသည်
async def help_handler(event):
    await event.edit(COMMAND_MENU)

@client.on(events.NewMessage(pattern=r'\.getid|\/getid', outgoing=True)) # outgoing=True ထည့်ထားသည်
async def getid_handler(event):
    user_id = event.sender_id
    chat_id = event.chat_id
    
    reply_to_id = None
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.sender:
            reply_to_id = replied_msg.sender_id

    text = f"👤 **Your User ID:** `{user_id}`\n"
    text += f"💬 **Chat ID:** `{chat_id}`\n"
    if reply_to_id:
        text += f"🎯 **Replied User ID:** `{reply_to_id}`"
        
    await event.edit(text)

# --- BOT CONTROL (Owner Only) ---

@client.on(events.NewMessage(pattern=r'\.stopbot|\/stopbot', outgoing=True))
async def stopbot_handler(event):
    global IS_BOT_RUNNING
    if not is_owner(event): return # Only Owner can stop the entire bot
    
    IS_BOT_RUNNING = False
    save_global_data_to_db()
    await event.edit("🔴 **Bot activities temporarily suspended.** Use `/startbot` to resume.")
    logging.warning("Bot activities suspended.")

@client.on(events.NewMessage(pattern=r'\.startbot|\/startbot', outgoing=True))
async def startbot_handler(event):
    global IS_BOT_RUNNING
    if not is_owner(event): return # Only Owner can start the entire bot
    
    IS_BOT_RUNNING = True
    save_global_data_to_db()
    await event.edit("🟢 **Bot activities resumed.**")
    logging.warning("Bot activities resumed.")

# --- PERSISTENT AUTO-REPLY COMMANDS (Admin/Owner) ---
# **ယခု Commands များသည် is_admin_or_owner ဖြင့် စစ်ဆေးထားသည်**

@client.on(events.NewMessage(pattern=r'\.addreply (.*) \| (.*)', outgoing=True))
async def add_reply_handler(event):
    if not is_admin_or_owner(event): return
    
    match = event.pattern_match.groups()
    trigger = match[0].strip()
    reply = match[1].strip()
    
    if save_reply_to_db(trigger, reply):
        await event.edit(f"✅ **Auto-Reply Added/Updated!**\nTrigger: `{trigger}`\nReply: `{reply}`")
    else:
        await event.edit("❌ **Error!** Could not save to Database.")

@client.on(events.NewMessage(pattern=r'\.delreply (.*)', outgoing=True))
async def delete_reply_handler(event):
    if not is_admin_or_owner(event): return
    
    trigger = event.pattern_match.group(1).strip()
    
    if remove_reply_from_db(trigger):
        await event.edit(f"🗑️ **Auto-Reply Deleted!**\nTrigger: `{trigger}`")
    else:
        await event.edit(f"❌ **Error!** Could not find or delete reply with trigger: `{trigger}`")

@client.on(events.NewMessage(pattern=r'\.listreplies', outgoing=True))
async def list_replies_handler(event):
    if not is_admin_or_owner(event): return
    
    if not AUTO_REPLIES:
        await event.edit("💡 No persistent auto-replies found in the database.")
        return
    
    reply_list = ""
    for i, (trigger, reply) in enumerate(AUTO_REPLIES.items()):
        if i >= 10:
            reply_list += "\n...(and more)"
            break
        reply_list += f"`{trigger}` -> `{reply[:30]}`...\n"
        
    await event.edit(f"📋 **Persistent Auto-Replies ({len(AUTO_REPLIES)} Total):**\n\n{reply_list}")

# --- EXISTING AUTO-REPLY (TARGETING) COMMANDS (Admin/Owner) ---

@client.on(events.NewMessage(pattern=r'ဟျောင့်ဝက်မကိုက်လေ', outgoing=True))
async def existing_reply_start_handler(event):
    if not is_admin_or_owner(event): return
    
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.sender:
            target_user_id = replied_msg.sender_id
            
            triggers = ["ဟျောင့်ဝက်မကိုက်လေ", "ဘာလဲ", "ဘယ်လဲ"] 
            EXISTING_REPLY_TARGETS[target_user_id] = triggers
            save_global_data_to_db()
            
            await event.edit(f"🐷 **Existing Reply Target Set!** User ID: `{target_user_id}`\nTriggers: {', '.join(triggers)}")
    else:
        await event.edit("❌ Please reply to a message to set the target.")

@client.on(events.NewMessage(pattern=r'သေလိုက်', outgoing=True))
async def existing_reply_stop_handler(event):
    if not is_admin_or_owner(event): return
    
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.sender and replied_msg.sender_id in EXISTING_REPLY_TARGETS:
            target_user_id = replied_msg.sender_id
            del EXISTING_REPLY_TARGETS[target_user_id]
            save_global_data_to_db()
            await event.edit(f"☠️ **Existing Reply Target Removed!** User ID: `{target_user_id}`")
        else:
            await event.edit("💡 That user was not a reply target.")
    else:
        EXISTING_REPLY_TARGETS.clear()
        save_global_data_to_db()
        await event.edit("🧹 **Existing Reply Targets Cleared** (Global).")

# --- AUTO-DELETE COMMANDS (Admin/Owner) ---

@client.on(events.NewMessage(pattern=r'(\.ကန်|\/ကန်)', outgoing=True))
@client.on(events.NewMessage(pattern=r'(\.autodelete|\/autodelete)(?: @)?(\w+)?', outgoing=True))
async def autodelete_add_handler(event):
    if not is_admin_or_owner(event): return
    
    chat_id = str(event.chat_id)
    target_user = None

    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.sender:
            target_user = str(replied_msg.sender_id)
    elif event.pattern_match.group(2):
        try:
            target_entity = await client.get_entity(event.pattern_match.group(2))
            target_user = str(target_entity.id)
        except Exception:
            await event.edit("❌ User not found or invalid format.")
            return

    if target_user:
        if chat_id not in AUTO_DELETE_USERS:
            AUTO_DELETE_USERS[chat_id] = {}
        
        AUTO_DELETE_USERS[chat_id][target_user] = 0
        save_global_data_to_db()
        await event.edit(f"🗑️ **Auto-Delete Enabled** for user ID: `{target_user}` in this chat.")
    else:
        await event.edit("❌ Please reply to a user's message or use `/autodelete @username`.")


@client.on(events.NewMessage(pattern=r'(\.stopautodelete|\/stopautodelete)(?: @)?(\w+)?', outgoing=True))
async def autodelete_remove_handler(event):
    if not is_admin_or_owner(event): return
    
    chat_id = str(event.chat_id)
    target_user = None

    if event.pattern_match.group(2):
        try:
            target_entity = await client.get_entity(event.pattern_match.group(2))
            target_user = str(target_entity.id)
        except Exception:
            await event.edit("❌ User not found or invalid format.")
            return

    if target_user:
        if chat_id in AUTO_DELETE_USERS and target_user in AUTO_DELETE_USERS[chat_id]:
            del AUTO_DELETE_USERS[chat_id][target_user]
            if not AUTO_DELETE_USERS[chat_id]:
                del AUTO_DELETE_USERS[chat_id]
            save_global_data_to_db()
            await event.edit(f"✅ **Auto-Delete Disabled** for user ID: `{target_user}` in this chat.")
        else:
            await event.edit("💡 That user was not set for auto-delete in this chat.")
    elif chat_id in AUTO_DELETE_USERS:
        del AUTO_DELETE_USERS[chat_id]
        save_global_data_to_db()
        await event.edit("✅ **Auto-Delete Disabled** for ALL users in this chat.")
    else:
        await event.edit("💡 No auto-delete users found for this chat.")

# --- AUTO-MENTION COMMANDS (Admin/Owner) ---

@client.on(events.NewMessage(pattern=r'(\.setmentioninterval|\/setmentioninterval) (\d+)', outgoing=True))
async def set_mention_interval_handler(event):
    global MENTION_INTERVAL
    if not is_admin_or_owner(event): return
    
    try:
        seconds = int(event.pattern_match.group(2))
        if 5 <= seconds <= 3600:
            MENTION_INTERVAL = seconds
            save_global_data_to_db()
            await event.edit(f"⏱️ **Mention Interval set to {seconds} seconds.**")
        else:
            await event.edit("❌ Interval must be between 5 and 3600 seconds.")
    except:
        await event.edit("❌ Invalid format. Use: `/setmentioninterval [seconds]`")

@client.on(events.NewMessage(pattern=r'\.stopallmentions|\/stopallmentions', outgoing=True))
async def stop_all_mentions_global_handler(event):
    global AUTO_MENTION_USERS
    if not is_admin_or_owner(event): return
    
    AUTO_MENTION_USERS.clear()
    save_global_data_to_db()
    await event.edit("🛑 **Global Auto-Mention Stopped** (All Chats).")

@client.on(events.NewMessage(pattern=r'(\.stopmention|\/stopmention)', outgoing=True))
async def stop_mention_handler(event):
    if not is_admin_or_owner(event): return
    
    chat_id = str(event.chat_id)
    
    if event.is_reply:
        replied_msg = await event.get_reply_message()
        if replied_msg and replied_msg.sender and chat_id in AUTO_MENTION_USERS and str(replied_msg.sender_id) in AUTO_MENTION_USERS[chat_id]:
            del AUTO_MENTION_USERS[chat_id][str(replied_msg.sender_id)]
            if not AUTO_MENTION_USERS[chat_id]:
                del AUTO_MENTION_USERS[chat_id]
            save_global_data_to_db()
            await event.edit(f"✅ **Auto-Mention Stopped** for User ID: `{replied_msg.sender_id}` in this chat.")
        else:
            await event.edit("💡 That user was not being auto-mentioned in this chat.")
    elif chat_id in AUTO_MENTION_USERS:
        del AUTO_MENTION_USERS[chat_id]
        save_global_data_to_db()
        await event.edit("✅ **Auto-Mention Stopped** for ALL users in this chat.")
    else:
        await event.edit("💡 No users are currently being auto-mentioned in this chat.")

@client.on(events.NewMessage(pattern=r'\.listmentions|\/listmentions', outgoing=True))
async def list_mentions_handler(event):
    if not is_admin_or_owner(event): return
    
    chat_id = str(event.chat_id)
    
    if chat_id not in AUTO_MENTION_USERS or not AUTO_MENTION_USERS[chat_id]:
        await event.edit("💡 No users are currently being auto-mentioned in this chat.")
        return
        
    user_list = "👥 **Auto-Mention Users in this Chat:**\n\n"
    for user_id_str in AUTO_MENTION_USERS[chat_id]:
        user_id = int(user_id_str)
        try:
            user_entity = await client.get_entity(user_id)
            user_name = get_display_name(user_entity)
            user_list += f"- `{user_name}` (`{user_id}`)\n"
        except Exception:
            user_list += f"- Unknown User (`{user_id}`)\n"
            
    await event.edit(user_list)

# ==============================================================================
# 5. Core Logic Handlers (Auto Delete, Auto Reply, Auto Mention)
# ==============================================================================

@client.on(events.NewMessage(incoming=True))
async def main_logic_handler(event):
    if not IS_BOT_RUNNING:
        return
    
    sender_id = event.sender_id
    chat_id = str(event.chat_id)
    
    # 1. PERSISTENT AUTO-REPLY Logic
    # Owner/Admin မဟုတ်သော Message များကိုသာ Reply ပြန်ရန်
    if event.text in AUTO_REPLIES and sender_id != OWNER_ID and sender_id not in ADMIN_IDS:
        await event.reply(AUTO_REPLIES[event.text])
        logging.info(f"📤 Sent persistent auto-reply for: '{event.text}'")
        return

    # 2. AUTO-DELETE Logic
    if chat_id in AUTO_DELETE_USERS and str(sender_id) in AUTO_DELETE_USERS[chat_id]:
        # Owner/Admin မဟုတ်သော Message များကိုသာ Delete လုပ်ရန်
        if sender_id != OWNER_ID and sender_id not in ADMIN_IDS:
            try:
                await event.delete()
                AUTO_DELETE_USERS[chat_id][str(sender_id)] += 1
                logging.info(f"🗑️ Deleted message from {sender_id} in chat {chat_id}.")
                return
            except Exception as e:
                logging.error(f"Failed to delete message: {e}")

    # 3. EXISTING AUTO-REPLY Logic
    # Owner/Admin မဟုတ်သော Message များကိုသာ Reply ပြန်ရန်
    if sender_id in EXISTING_REPLY_TARGETS and sender_id != OWNER_ID and sender_id not in ADMIN_IDS:
        if event.text in EXISTING_REPLY_TARGETS[sender_id]:
            try:
                owner_name = get_display_name(await client.get_me())
                await event.reply(f"ဟုတ်ကဲ့ပါ၊ ကျွန်တော် {owner_name} ကိုယ်စား ပြန်ဖြေပေးတာပါ။")
                return
            except Exception as e:
                logging.error(f"Failed to send existing auto-reply: {e}")

# ==============================================================================
# 6. Background Tasks (Keep-Alive & Auto-Mention)
# ==============================================================================

async def background_mention_task():
    """Background task to handle periodic auto-mentions."""
    while True:
        await asyncio.sleep(MENTION_INTERVAL)
        
        if not IS_BOT_RUNNING:
            continue
            
        current_time = time.time()
        
        save_global_data_to_db()

        for chat_id_str, targets in list(AUTO_MENTION_USERS.items()):
            chat_id = int(chat_id_str)
            for user_id_str, last_mention_time in list(targets.items()):
                user_id = int(user_id_str)
                
                if current_time - last_mention_time >= MENTION_INTERVAL:
                    try:
                        user_entity = await client.get_entity(user_id)
                        mention_handle = f"@{user_entity.username}" if user_entity.username else f"User ID: {user_id}"
                        
                        mention_text = f"🚨 {get_display_name(await client.get_me())} သည် {mention_handle} ကို သတိရနေပါသည်!"
                        await client.send_message(chat_id, mention_text)
                        
                        AUTO_MENTION_USERS[chat_id_str][user_id_str] = current_time
                        logging.info(f"🔔 Auto-mentioned user {user_id} in chat {chat_id}")
                    except Exception as e:
                        logging.error(f"Failed to auto-mention in chat {chat_id}: {e}")
        
        save_global_data_to_db()


app = Flask(__name__)

@app.route('/')
def home():
    """Simple health check endpoint."""
    return f"User Bot is running. Status: {'RUNNING' if IS_BOT_RUNNING else 'SUSPENDED'} | Persistence: MongoDB"

def keep_alive():
    """Periodically pings the RENDER_URL to prevent sleep."""
    while True:
        try:
            requests.get(RENDER_URL, timeout=10)
            logging.warning("✅ Pinged self to stay alive")
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Ping failed: {e}")
        time.sleep(300)

def run_flask():
    """Starts the Flask server in a separate thread."""
    port = int(os.environ.get('PORT', 5000))  
    app.run(host='0.0.0.0', port=port, debug=False)

# ==============================================================================
# 7. Main Execution Block
# ==============================================================================

async def main():
    """The main entry point for the Telethon client."""
    # Flask & Keep-Alive ကို Background မှာ စတင်
    threading.Thread(target=run_flask).start()
    threading.Thread(target=keep_alive).start()
    
    # Database မှ Data အားလုံးကို Load လုပ်ပါ
    load_data_from_db()
    
    await client.start()

    if not SESSION_STRING:
        session_string = client.session.save()
        # OWNER_ID သည် Integer တစ်ခုတည်းသာဖြစ်၍ တိုက်ရိုက် ပို့နိုင်သည်
        await client.send_message(OWNER_ID, f"⚠️ **New Session String Generated!**\n\n`{session_string}`\n\n**Please save this string and update the `BOT_SESSION` Environment Variable for future restarts!**")
        logging.warning(f"--- NEW SESSION STRING ---\n{session_string}\n--------------------------")

    # Background Mention Task ကို စတင်
    asyncio.create_task(background_mention_task())

    await client.send_message(OWNER_ID, "✅ **Userbot Client Started Successfully!**\n\n**Data Persistence: MongoDB**")
    logging.warning("🚀 Userbot is running and listening for events.")

    await client.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"An unexpected error occurred during startup: {e}")

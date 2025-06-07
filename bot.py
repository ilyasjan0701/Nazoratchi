import json
import os
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, 
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    ChatMember, Message
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from telegram.constants import ChatType, ChatMemberStatus
from telegram.error import TelegramError

# Bot konfiguratsiyasi
BOT_TOKEN = "7488874639:AAHcbmIp7Gq78HY1MVUrEaCHhRwQyvxRCt8"
OWNER_ID = 7090133560  # Bot egasining user ID si
MANDATORY_CHANNEL = "@diqqatmarkazida1"  # Majburiy obuna kanali

# Ma'lumotlar fayllari
GROUPS_FILE = "groups.json"
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"
ADMIN_POSTS_FILE = "admin_posts.json"

class TelegramBot:
    def __init__(self):
        self.groups_data = self.load_json(GROUPS_FILE, {})
        self.users_data = self.load_json(USERS_FILE, {})
        self.channels_data = self.load_json(CHANNELS_FILE, {})
        self.admin_posts = self.load_json(ADMIN_POSTS_FILE, {})
        
    def load_json(self, filename: str, default: dict) -> dict:
        """JSON fayldan ma'lumotlarni yuklash"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Xatolik {filename} faylni yuklashda: {e}")
        return default
    
    def save_json(self, filename: str, data: dict):
        """Ma'lumotlarni JSON faylga saqlash"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Xatolik {filename} faylga saqlashda: {e}")
    
    def save_group(self, group_id: int, group_data: dict):
        """Guruh ma'lumotlarini saqlash"""
        self.groups_data[str(group_id)] = group_data
        self.save_json(GROUPS_FILE, self.groups_data)
    
    def save_user(self, user_id: int, user_data: dict):
        """Foydalanuvchi ma'lumotlarini saqlash"""
        self.users_data[str(user_id)] = user_data
        self.save_json(USERS_FILE, self.users_data)
    
    def save_channels(self):
        """Kanallar ma'lumotlarini saqlash"""
        self.save_json(CHANNELS_FILE, self.channels_data)
    
    def save_admin_posts(self):
        """Admin postlarini saqlash"""
        self.save_json(ADMIN_POSTS_FILE, self.admin_posts)

# Bot instansiyasi
bot_instance = TelegramBot()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    user_id = update.effective_user.id
    chat_type = update.effective_chat.type
    
    if chat_type != ChatType.PRIVATE:
        return
    
    if user_id == OWNER_ID:
        keyboard = [
            [KeyboardButton("ðŸ“Š Statistika"), KeyboardButton("ðŸ“¢ Xabar yuborish")],
            [KeyboardButton("ðŸ‘¥ Guruhlarni ko'rish"), KeyboardButton("âš™ï¸ Sozlamalar")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "ðŸ”¥ Salom, bot egasi!\n\n"
            "ðŸ“Š Statistika - bot statistikalarini ko'rish\n"
            "ðŸ“¢ Xabar yuborish - barcha guruhlarga xabar yuborish\n"
            "ðŸ‘¥ Guruhlarni ko'rish - ulangan guruhlar ro'yxati\n"
            "âš™ï¸ Sozlamalar - bot sozlamalari",
            reply_markup=reply_markup
        )
    else:
        # Guruh adminlari uchun
        keyboard = [
            [KeyboardButton("âž• Guruh qo'shish")],
            [KeyboardButton("ðŸ“‹ Mening guruhlarim"), KeyboardButton("ðŸ“º Kanal sozlash")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "ðŸ‘‹ Assalomu alaykum!\n\n"
            "ðŸ¤– Men guruhlarni boshqaruvchi botman. Men quyidagi vazifalarni bajaraman:\n\n"
            "âœ… Majburiy obuna nazorati\n"
            "ðŸš« Reklama havolalarni o'chirish\n"
            "ðŸ›¡ï¸ Zararli .apk fayllarni o'chirish\n"
            "ðŸ“Š Guruh faoliyatini nazorat qilish\n\n"
            "Botdan foydalanish uchun quyidagi tugmalardan foydalaning:",
            reply_markup=reply_markup
        )

async def handle_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Matn xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    text = update.message.text
    chat_type = update.effective_chat.type
    
    if chat_type == ChatType.PRIVATE:
        if user_id == OWNER_ID:
            await handle_owner_messages(update, context)
        else:
            await handle_user_messages(update, context)
    else:
        await handle_group_messages(update, context)

async def handle_owner_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot egasi xabarlarini qayta ishlash"""
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "ðŸ“Š Statistika":
        total_groups = len(bot_instance.groups_data)
        total_users = len(bot_instance.users_data)
        
        await update.message.reply_text(
            f"ðŸ“Š Bot statistikasi:\n\n"
            f"ðŸ‘¥ Ulangan guruhlar: {total_groups}\n"
            f"ðŸ‘¤ Foydalanuvchilar: {total_users}\n"
            f"ðŸ“… Oxirgi yangilanish: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )
    
    elif text == "ðŸ“¢ Xabar yuborish":
        context.user_data['sending_broadcast'] = True
        context.user_data['broadcast_messages'] = []
        
        await update.message.reply_text(
            "ðŸ“ Barcha guruhlarga yubormoqchi bo'lgan xabaringizni yuboring.\n"
            "Bu matn, rasm, video yoki boshqa fayl bo'lishi mumkin.\n\n"
            "/korish - xabar postini ko'rish\n"
            "/yubor - xabarni yuborish\n"
            "/qaytar - bekor qilish"
        )
    
    elif text == "ðŸ‘¥ Guruhlarni ko'rish":
        if not bot_instance.groups_data:
            await update.message.reply_text("âŒ Hozircha birorta guruh ulanmagan.")
            return
        
        keyboard = []
        for group_id, group_info in bot_instance.groups_data.items():
            group_name = group_info.get('title', f'Guruh {group_id}')
            keyboard.append([InlineKeyboardButton(
                f"ðŸ‘¥ {group_name}", 
                callback_data=f"group_info_{group_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "ðŸ‘¥ Ulangan guruhlar ro'yxati:",
            reply_markup=reply_markup
        )
    
    elif context.user_data.get('sending_broadcast'):
        await handle_broadcast_content(update, context)
from telegram import KeyboardButton, KeyboardButtonRequestChat, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

async def handle_user_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oddiy foydalanuvchi xabarlarini qayta ishlash"""
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "➕ Guruh qo'shish":
        # TO'G'RI usul - KeyboardButtonRequestChat obyektini ishlatish
        keyboard = [[KeyboardButton(
            "📤 Guruhlarni ulashish", 
            request_chat=KeyboardButtonRequestChat(
                request_id=1,
                chat_is_channel=False,
                chat_is_forum=None,
                chat_has_username=None,
                chat_is_created=None,
                user_administrator_rights=None,
                bot_administrator_rights=None,
                bot_is_member=None
            )
        )]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        
        await update.message.reply_text(
            "📤 Quyidagi tugma orqali bot qo'shmoqchi bo'lgan guruhingizni tanlang:",
            reply_markup=reply_markup
        )
    
    elif text == "📋 Mening guruhlarim":
        user_groups = []
        for group_id, group_info in bot_instance.groups_data.items():
            if str(user_id) in group_info.get('admins', []):
                user_groups.append((group_id, group_info))
        
        if not user_groups:
            await update.message.reply_text("⌛ Sizda hozircha guruhlar yo'q.")
            return
        
        keyboard = []
        for group_id, group_info in user_groups:
            group_name = group_info.get('title', f'Guruh {group_id}')
            keyboard.append([InlineKeyboardButton(
                f"👥 {group_name}",
                callback_data=f"my_group_{group_id}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "📋 Sizning guruhlaringiz:",
            reply_markup=reply_markup
        )
    
    elif text == "📺 Kanal sozlash":
        await update.message.reply_text(
            "📺 Kanal sozlash uchun avval guruhingizni tanlang.\n"
            "📋 'Mening guruhlarim' tugmasini bosing."
        )
async def handle_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guruh xabarlarini qayta ishlash"""
    message = update.message
    user = update.effective_user
    chat = update.effective_chat
    
    # Guruh ma'lumotlarini saqlash
    group_data = {
        'title': chat.title,
        'type': chat.type,
        'added_date': datetime.now().isoformat(),
        'admins': [],
        'mandatory_channels': [MANDATORY_CHANNEL]  # Standart majburiy kanal
    }
    
    if str(chat.id) not in bot_instance.groups_data:
        bot_instance.save_group(chat.id, group_data)
    
    # Majburiy obuna tekshirish
    if not await check_subscription(user.id, context):
        try:
            await message.delete()
            warning_msg = await message.reply_text(
                f"âš ï¸ {user.first_name}, guruhda yozish uchun kanalga obuna bo'ling!\n\n"
                f"ðŸ“º Kanal: {MANDATORY_CHANNEL}\n\n"
                f"Obuna bo'lgandan keyin qaytadan yozing.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("ðŸ“º Kanalga o'tish", url=f"https://t.me/{MANDATORY_CHANNEL[1:]}")
                ]])
            )
            # Ogohlantirish xabarini 30 soniyadan keyin o'chirish
            context.job_queue.run_once(
                lambda context: context.bot.delete_message(chat.id, warning_msg.message_id),
                30
            )
        except Exception:
            pass
        return
    
    # Reklama havolalarni tekshirish
    if message.text and is_advertisement_link(message.text):
        try:
            await message.delete()
            warning_msg = await message.reply_text(
                f"ðŸš« {user.first_name}, reklama havolalar taqiqlanadi!\n"
                f"Iltimos, reklama tarqatmang!",
                reply_to_message_id=None
            )
            context.job_queue.run_once(
                lambda context: context.bot.delete_message(chat.id, warning_msg.message_id),
                15
            )
        except Exception:
            pass
        return
    
    # .apk fayllarni tekshirish
    if message.document and message.document.file_name:
        if message.document.file_name.lower().endswith('.apk'):
            try:
                await message.delete()
                warning_msg = await message.reply_text(
                    f"âš ï¸ {user.first_name}, APK fayllar xavfli bo'lishi mumkin!\n"
                    f"Zararli virusli fayllar tarqatmang!",
                    reply_to_message_id=None
                )
                context.job_queue.run_once(
                    lambda context: context.bot.delete_message(chat.id, warning_msg.message_id),
                    20
                )
            except Exception:
                pass
            return

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Majburiy obuna tekshirish"""
    try:
        member = await context.bot.get_chat_member(MANDATORY_CHANNEL, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

def is_advertisement_link(text: str) -> bool:
    """Reklama havolani aniqlash"""
    # URL pattern
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    telegram_pattern = r'@[a-zA-Z0-9_]+'
    
    # Reklama so'zlari
    ad_keywords = [
        'reklama', 'sotiladi', 'sotuvda', 'chegirma', 'aktsiya', 
        'bonus', 'tekin', 'bepul', 'http', 'www', 't.me'
    ]
    
    text_lower = text.lower()
    
    # URL yoki Telegram username bor-yo'qligini tekshirish
    if re.search(url_pattern, text) or re.search(telegram_pattern, text):
        # Reklama so'zlari bor-yo'qligini tekshirish
        for keyword in ad_keywords:
            if keyword in text_lower:
                return True
    
    return False

async def handle_broadcast_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Broadcast xabar kontentini qayta ishlash"""
    user_id = update.effective_user.id
    
    if update.message.text:
        if update.message.text == "/korish":
            if not context.user_data.get('broadcast_messages'):
                await update.message.reply_text("âŒ Hozircha xabar qo'shilmagan.")
                return
            
            await update.message.reply_text(
                f"ðŸ“‹ Joriy xabar posti ({len(context.user_data['broadcast_messages'])} ta xabar):\n\n"
                "Xabarlarni ko'rish uchun /yubor tugmasini bosing."
            )
            return
        
        elif update.message.text == "/yubor":
            if not context.user_data.get('broadcast_messages'):
                await update.message.reply_text("âŒ Yuborish uchun xabar qo'shing.")
                return
            
            await send_broadcast(update, context)
            return
        
        elif update.message.text == "/qaytar":
            context.user_data['sending_broadcast'] = False
            context.user_data['broadcast_messages'] = []
            await update.message.reply_text("âœ… Operatsiya bekor qilindi.")
            return
    
    # Xabarni saqlash
    if 'broadcast_messages' not in context.user_data:
        context.user_data['broadcast_messages'] = []
    
    context.user_data['broadcast_messages'].append({
        'type': 'message',
        'content': update.message,
        'message_id': update.message.message_id
    })
    
    await update.message.reply_text(
        f"âœ… Xabar postga qo'shildi ({len(context.user_data['broadcast_messages'])} ta xabar).\n\n"
        "/korish â€” xabar postini ko'rish\n"
        "/yubor â€” xabarni yuborish\n"
        "/qaytar â€” bekor qilish"
    )

async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha guruhlarga xabar yuborish"""
    if not bot_instance.groups_data:
        await update.message.reply_text("âŒ Guruhlar topilmadi.")
        return
    
    messages = context.user_data.get('broadcast_messages', [])
    if not messages:
        await update.message.reply_text("âŒ Yuborish uchun xabar yo'q.")
        return
    
    status_msg = await update.message.reply_text("ðŸ“¤ Xabar yuborilmoqda...")
    
    success_count = 0
    failed_count = 0
    
    for group_id in bot_instance.groups_data.keys():
        try:
            for msg_data in messages:
                original_msg = msg_data['content']
                
                if original_msg.text:
                    await context.bot.send_message(int(group_id), original_msg.text)
                elif original_msg.photo:
                    await context.bot.send_photo(
                        int(group_id), 
                        original_msg.photo[-1].file_id,
                        caption=original_msg.caption
                    )
                elif original_msg.video:
                    await context.bot.send_video(
                        int(group_id),
                        original_msg.video.file_id,
                        caption=original_msg.caption
                    )
                elif original_msg.document:
                    await context.bot.send_document(
                        int(group_id),
                        original_msg.document.file_id,
                        caption=original_msg.caption
                    )
            
            success_count += 1
            await asyncio.sleep(0.1)  # Rate limiting
            
        except Exception as e:
            failed_count += 1
            print(f"Guruhga yuborishda xatolik {group_id}: {e}")
    
    await status_msg.edit_text(
        f"âœ… Xabar yuborish yakunlandi!\n\n"
        f"ðŸ“¤ Muvaffaqiyatli: {success_count}\n"
        f"âŒ Xatolik: {failed_count}"
    )
    
    # Ma'lumotlarni tozalash
    context.user_data['sending_broadcast'] = False
    context.user_data['broadcast_messages'] = []

async def callback_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback query larni qayta ishlash"""

    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith("group_info_"):
        group_id = data.split("_")[-1]
        group_info = bot_instance.groups_data.get(group_id, {})
        
        text = f"ðŸ‘¥ Guruh: {group_info.get('title', 'Noma\'lum')}\n"
        text += f"ðŸ†” ID: {group_id}\n"
        text += f"ðŸ“… Qo'shilgan: {group_info.get('added_date', 'Noma\'lum')}\n"
        text += f"ðŸ“º Majburiy kanallar: {len(group_info.get('mandatory_channels', []))}"
        
        await query.edit_message_text(text)
    
    elif data.startswith("my_group_"):
        group_id = data.split("_")[-1]
        group_info = bot_instance.groups_data.get(group_id, {})
        
        keyboard = [
            [InlineKeyboardButton("ðŸ“º Kanal qo'shish", callback_data=f"add_channel_{group_id}")],
            [InlineKeyboardButton("ðŸ“‹ Kanallar ro'yxati", callback_data=f"list_channels_{group_id}")],
            [InlineKeyboardButton("ðŸ”™ Orqaga", callback_data="back_to_groups")]
        ]
        
        text = f"ðŸ‘¥ {group_info.get('title', 'Noma\'lum guruh')}\n\n"
        text += "Quyidagi amallarni tanlang:"
        
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    """Asosiy funksiya"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlar
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_messages))
    application.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.ALL, handle_text_messages))
    application.add_handler(CallbackQueryHandler(callback_query_handler))
    
    print("ðŸ¤– Bot ishga tushdi!")
    application.run_polling()

if __name__ == "__main__":
    main()

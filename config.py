# Bot konfiguratsiya fayli
# Bu faylni config.py nomi bilan saqlang va o'z ma'lumotlaringizni kiriting

# Bot Token - @BotFather dan olingan token
BOT_TOKEN = "7488874639:AAHcbmIp7Gq78HY1MVUrEaCHhRwQyvxRCt8"

# Bot egasining Telegram User ID si
# ID ni olish uchun @userinfobot ga /start yuboring
OWNER_ID = 7090133560

# Majburiy obuna kanali
MANDATORY_CHANNEL = "@diqqatmarkazida1"

# Ma'lumotlar fayllari
GROUPS_FILE = "data/groups.json"
USERS_FILE = "data/users.json" 
CHANNELS_FILE = "data/channels.json"
ADMIN_POSTS_FILE = "data/admin_posts.json"

# Reklama so'zlari ro'yxati (qo'shimcha)
SPAM_KEYWORDS = [
    'reklama', 'sotiladi', 'sotuvda', 'chegirma', 'aktsiya',
    'bonus', 'tekin', 'bepul', 'arzon', 'ishonchli',
<<<<<<< HEAD
    'tez', 'buyurtma', 'zakaz', 'Ð´Ð¾ÑÑ‚Ð°Ð²ÐºÐ°'
=======
    'tez', 'buyurtma', 'zakaz', 'доставка'
>>>>>>> d7639d9 (First commit)
]

# Taqiqlangan fayl turlari
FORBIDDEN_FILE_TYPES = ['.apk', '.exe', '.bat', '.scr', '.com']

# Xabar o'chirish vaqti (soniyalarda)
DELETE_WARNING_AFTER = 30  # Ogohlantirish xabarini o'chirish vaqti
DELETE_SPAM_WARNING_AFTER = 15  # Spam ogohlantirish xabarini o'chirish vaqti

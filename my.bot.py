from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "7719508112:AAFTdU-XdUiCYjWXKxaBYFgdn3DSaUazlnY"
ADMIN_ID = 8299735075  # <-- O'zingizni Telegram ID

permission = {}
users = {}

# =========================
# AVTO JAVOBLAR
auto_answers = {
    "menu_1": {
        "price": ("💰 Narxlar", "narxlar.jpg"),
    },
    "menu_3": {
        "today": ("🛫 Bugungi reyslar", "bugungi.jpg"),
        "tomorrow": ("🛬 Ertangi reyslar", "ertangi.jpg"),
    },
    "menu_7": {
        "click": ("💳 Click", "click.jpg"),
        "payme": ("💳 Payme", "payme.jpg"),
    }
}

# =========================
# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    users[user.id] = user.first_name

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")]
    ]

    await update.message.reply_text(
        "Tilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# MENU
async def language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("🛻 Yuk jo'natish", callback_data="menu_1")],
        [InlineKeyboardButton("🏨 Mehmonxona", callback_data="menu_2")],
        [InlineKeyboardButton("✈️ Reyslar", callback_data="menu_3")],
        [InlineKeyboardButton("📞 Operator", callback_data="menu_4")],
        [InlineKeyboardButton("🛫 Aeroport", callback_data="menu_5")],
        [InlineKeyboardButton("📊 Statistika", callback_data="menu_6")],
        [InlineKeyboardButton("💳 To'lov tizimi", callback_data="menu_7")]
    ]

    await query.edit_message_text(
        "Menyuni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# MENU TANLANGANDA
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = user.id
    selected_menu = query.data

    permission[user_id] = False

    keyboard = []

    if selected_menu in auto_answers:
        for key, value in auto_answers[selected_menu].items():
            keyboard.append([
                InlineKeyboardButton(
                    value[0],
                    callback_data=f"auto|{selected_menu}|{key}|{user_id}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("✅ Ruxsat berish", callback_data=f"allow|{user_id}")
    ])

    await context.bot.send_message(
        ADMIN_ID,
        f"📌 Yangi so'rov!\n\n"
        f"👤 {user.first_name}\n"
        f"🆔 {user_id}\n"
        f"📂 Tanlangan menyu: {selected_menu}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    await context.bot.send_message(
        user_id,
        "⏳ So'rovingiz adminga yuborildi. Javobni kuting."
    )

# =========================
# AVTO JAVOB
async def auto_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, menu, key, user_id = query.data.split("|")
    user_id = int(user_id)

    title, content = auto_answers[menu][key]

    try:
        with open(content, "rb") as photo:
            await context.bot.send_photo(user_id, photo)
    except:
        await context.bot.send_message(user_id, content)

    await query.answer("Yuborildi ✅")

# =========================
# RUXSAT
async def allow_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, user_id = query.data.split("|")
    user_id = int(user_id)

    permission[user_id] = True
    await context.bot.send_message(user_id, "✅ Sizga yozish ruxsati berildi.")
    await query.answer("Ruxsat berildi")

# =========================
# ADMIN PANEL
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if not users:
        await update.message.reply_text("Foydalanuvchilar yo'q.")
        return

    keyboard = []
    for user_id, name in users.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{name} ({user_id})",
                callback_data=f"chat|{user_id}"
            )
        ])

    await update.message.reply_text(
        "Foydalanuvchini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# =========================
# ADMIN USER TANLASH
async def chat_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, user_id = query.data.split("|")
    context.user_data["active_user"] = int(user_id)

    await query.edit_message_text(
        f"Tanlandi: {users[int(user_id)]}"
    )

# =========================
# XABARLAR
async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    is_admin = user_id == ADMIN_ID

    if is_admin:
        active = context.user_data.get("active_user")
        if not active:
            await update.message.reply_text("Avval /admin orqali user tanlang.")
            return

        await context.bot.copy_message(
            active,
            update.message.chat_id,
            update.message.message_id
        )
        return

    if not permission.get(user_id):
        await update.message.reply_text("❗ Admin ruxsatini kuting.")
        return

    await context.bot.copy_message(
        ADMIN_ID,
        update.message.chat_id,
        update.message.message_id
    )

    await update.message.reply_text("✅ Xabaringiz yuborildi.")

# =========================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))

app.add_handler(CallbackQueryHandler(language_handler, pattern="^lang_"))
app.add_handler(CallbackQueryHandler(menu_handler, pattern="^menu_"))
app.add_handler(CallbackQueryHandler(auto_handler, pattern="^auto"))
app.add_handler(CallbackQueryHandler(allow_handler, pattern="^allow"))
app.add_handler(CallbackQueryHandler(chat_select, pattern="^chat"))

app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, messages))

app.run_polling()

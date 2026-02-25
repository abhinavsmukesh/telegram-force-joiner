import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==============================
# 🔐 ADD YOUR DETAILS HERE
# ==============================

BOT_TOKEN = "8777999221:AAEU_Ug0ljN-7rKm9dAZJ6NjRbL26Uy2Vdk"
CHANNEL_USERNAME = "swiggytrick"  # WITHOUT @

# ==============================
# Logging
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==============================
# FORCE JOIN CHECK
# ==============================

async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.effective_chat.id

    if user.is_bot:
        return

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status not in ["member", "administrator", "creator"]:

            # Delete user's message
            await update.message.delete()

            # Clickable mention
            mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📢 Subscribe to channel",
                        url=f"https://t.me/{CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ OK | I subscribed",
                        callback_data="verify_join"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                f"{mention} to be accepted in the group, "
                f"please subscribe to our channel.\n"
                f"Once joined, click the button below.\n\n"
                f"Action: Muted 🔇"
            )

            await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

    except Exception as e:
        logging.error(e)


# ==============================
# VERIFY BUTTON
# ==============================

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    member = await context.bot.get_chat_member(
        f"@{CHANNEL_USERNAME}",
        user.id
    )

    if member.status in ["member", "administrator", "creator"]:
        await query.answer("✅ Verified! You can now chat.")
        await query.message.edit_text(
            "✅ You are verified and can now send messages."
        )
    else:
        await query.answer("❌ Please join the channel first.", show_alert=True)


# ==============================
# MAIN
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, force_join))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))

    print("Force Join Bot Running...")
    app.run_polling()


if name == "main":
    main()

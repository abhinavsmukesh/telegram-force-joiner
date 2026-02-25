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

BOT_TOKEN = "8777999221:AAHGxKFOmKg4WhtdUT1dA2jt8DHjNG6fjM4"
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
    message = update.effective_message

    if not user or user.is_bot or not message:
        return

    chat_id = message.chat_id

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status not in ["member", "administrator", "creator"]:

            # Delete user message
            await message.delete()

            # Proper clickable mention
            if user.username:
                display_name = f"@{user.username}"
            else:
                display_name = user.first_name

            mention = f'<a href="tg://user?id={user.id}">{display_name}</a>'

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
                f"{mention} to be accepted in the group,\n"
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

    await query.answer()

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status in ["member", "administrator", "creator"]:
            await query.message.edit_text(
                "✅ You are verified and can now send messages."
            )
        else:
            await query.answer("❌ Please join the channel first.", show_alert=True)

    except Exception as e:
        logging.error(e)


# ==============================
# MAIN
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, force_join)
    )
    app.add_handler(
        CallbackQueryHandler(verify_join, pattern="verify_join")
    )

    print("Force Join Bot Running...")
    app.run_polling()


if __name__ == "main":
    main()

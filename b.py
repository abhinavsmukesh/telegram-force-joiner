import os
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
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

BOT_TOKEN = "8777999221:AAEU_u9yAgkq9zAD5YpJDdRVWs2AgTf6DT4"  # <-- PUT YOUR TOKEN HERE

CHANNEL_USERNAME = "swiggytrick"  
# 👆 WITHOUT @

# ==============================
# Logging
# ==============================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

# ==============================
# FORCE JOIN CHECK (Every Message)
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

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ I Joined",
                        callback_data="verify_join"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            await context.bot.send_message(
                chat_id=chat_id,
                text="🔒 You must join our channel to send messages in this group.",
                reply_markup=reply_markup
            )

    except Exception as e:
        logging.error(e)

# ==============================
# Verify Button
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
        await query.message.edit_text("✅ You are verified and can now send messages.")
    else:
        await query.answer("❌ Please join the channel first.", show_alert=True)

# ==============================
# Main
# ==============================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, force_join))
    app.add_handler(CallbackQueryHandler(verify_join, pattern="verify_join"))

    print("Force Join Bot Running...")
    app.run_polling()

if __name__ == "__main__":
    main()
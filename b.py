import os
import asyncio
import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
)
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==========================
# CONFIG
# ==========================

BOT_TOKEN = os.getenv("8777999221:AAHGxKFOmKg4WhtdUT1dA2jt8DHjNG6fjM4")
CHANNEL_USERNAME = "swiggytrick"  # without @
WARNING_DELETE_TIME = 20

# ==========================
# LOGGING
# ==========================

logging.basicConfig(level=logging.INFO)

# ==========================
# FORCE JOIN
# ==========================

async def force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    message = update.effective_message
    chat = update.effective_chat

    if not user or user.is_bot or not message:
        return

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status not in ["member", "administrator", "creator"]:

            # Mute user
            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )

            # Delete user message
            await message.delete()

            # 🔥 SIMPLE AND WORKING MENTION
            mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'

            text = (
                f"{mention} to be accepted in the group, "
                f"please subscribe to our channel.\n\n"
                f"Once joined, click the button below.\n\n"
                f"<b>Action:</b> Muted 🔇"
            )

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

            warning = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

            await asyncio.sleep(WARNING_DELETE_TIME)

            try:
                await warning.delete()
            except:
                pass

    except Exception as e:
        logging.error(e)

# ==========================
# VERIFY BUTTON
# ==========================

async def verify_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    chat = query.message.chat

    await query.answer()

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status in ["member", "administrator", "creator"]:

            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )

            await query.message.edit_text(
                "✅ Verification Successful!\n\n"
                "You can now send messages."
            )

        else:
            await query.answer(
                "❌ Please join the channel first.",
                show_alert=True
            )

    except Exception as e:
        logging.error(e)

# ==========================
# MAIN
# ==========================

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, force_join)
    )

    app.add_handler(
        CallbackQueryHandler(verify_join, pattern="verify_join")
    )

    print("Force Join Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()

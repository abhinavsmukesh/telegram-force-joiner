import logging
import asyncio
from html import escape

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

# ==============================
# 🔐 CONFIGURATION
# ==============================

BOT_TOKEN = "8777999221:AAHGxKFOmKg4WhtdUT1dA2jt8DHjNG6fjM4"
CHANNEL_USERNAME = "swiggytrick"  # WITHOUT @
WARNING_DELETE_TIME = 20  # seconds

# ==============================
# LOGGING
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
    chat = update.effective_chat

    if not user or not message or user.is_bot:
        return

    try:
        member = await context.bot.get_chat_member(
            f"@{CHANNEL_USERNAME}",
            user.id
        )

        if member.status not in ["member", "administrator", "creator"]:

            # 🔇 Restrict user (real mute)
            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )

            # Delete user's message
            await message.delete()

            # Safe display name
            if user.username:
                display_name = "@" + escape(user.username)
            else:
                display_name = escape(user.full_name)

            mention = f'<a href="tg://user?id={user.id}">{display_name}</a>'

            keyboard = [
                [
                    InlineKeyboardButton(
                        "📢 Join Channel",
                        url=f"https://t.me/{CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "✅ I Have Joined",
                        callback_data="verify_join"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)

            text = (
                f"🔒 <b>Membership Required</b>\n\n"
                f"{mention}, to participate in this group,\n"
                f"please subscribe to our official channel.\n\n"
                f"After joining, press the button below.\n\n"
                f"🔇 <b>Status:</b> Muted"
            )

            warning = await context.bot.send_message(
                chat_id=chat.id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )

            # Auto delete warning after X seconds
            await asyncio.sleep(WARNING_DELETE_TIME)
            try:
                await warning.delete()
            except:
                pass

    except Exception as e:
        logging.error(f"Force join error: {e}")

# ==============================
# VERIFY BUTTON
# ==============================

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

            # 🔓 Unmute user
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
                "✅ <b>Verification Successful</b>\n\n"
                "You can now send messages in this group.",
                parse_mode=ParseMode.HTML
            )

        else:
            await query.answer(
                "❌ Please join the channel first.",
                show_alert=True
            )

    except Exception as e:
        logging.error(f"Verify error: {e}")

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

    print("🚀 Professional Force Join Bot Running...")
    app.run_polling()

if __name__ == "main":
    main()

"""
==================================================
  Professional Telegram Force Join Bot
==================================================

FEATURES:
✔ Force channel join before messaging
✔ Auto mute non-members
✔ Clean HTML mention (real name)
✔ Auto-delete warning message
✔ Secure environment variable token
✔ Production-ready logging
==================================================
"""

import os
import asyncio
import logging
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
    filters,
)

# ==================================================
# 🔐 CONFIGURATION (EDIT THESE ONLY)
# ==================================================

BOT_TOKEN = os.getenv("8777999221:AAHGxKFOmKg4WhtdUT1dA2jt8DHjNG6fjM4")  # Set in Render/VPS
CHANNEL_USERNAME = "swiggytrick"  # WITHOUT @
WARNING_DELETE_TIME = 20  # Seconds before warning auto deletes

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# ==================================================
# FORCE JOIN CHECK (Runs on every message)
# ==================================================

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

            # 🔇 Restrict (mute)
            await context.bot.restrict_chat_member(
                chat.id,
                user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )

            # Delete user message
            await message.delete()

            # Proper clickable name mention
            safe_name = escape(user.full_name)
            mention = f'<a href="tg://user?id={user.id}">{safe_name}</a>'

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
                f"🔒 <b>Channel Membership Required</b>\n\n"
                f"{mention}, you must join our official channel "
                f"to send messages in this group.\n\n"
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

            # Auto-delete warning
            await asyncio.sleep(WARNING_DELETE_TIME)
            try:
                await warning.delete()
            except:
                pass

    except Exception as e:
        logger.error(f"Force join error: {e}")

# ==================================================
# VERIFY BUTTON HANDLER
# ==================================================

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

            # 🔓 Unmute
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
        logger.error(f"Verification error: {e}")

# ==================================================
# MAIN APPLICATION
# ==================================================

def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN environment variable not set!")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(
        MessageHandler(filters.ALL & ~filters.StatusUpdate.ALL, force_join)
    )

    app.add_handler(
        CallbackQueryHandler(verify_join, pattern="verify_join")
    )

    logger.info("🚀 Professional Force Join Bot Running...")
    app.run_polling()

# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()

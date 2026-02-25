"""
=============================================
   PROFESSIONAL TELEGRAM FORCE JOIN BOT
=============================================

✔ Forces channel membership
✔ Deletes messages from non-members
✔ Mutes non-members
✔ Proper clickable name mention
✔ Clean & stable implementation
=============================================
"""

import os
import asyncio
import logging

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions,
    MessageEntity
)

from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ==================================================
# 🔐 CONFIGURATION
# ==================================================

BOT_TOKEN = os.getenv("8777999221:AAHGxKFOmKg4WhtdUT1dA2jt8DHjNG6fjM4")  # Set this in Render/VPS
CHANNEL_USERNAME = "swiggytrick"   # WITHOUT @
WARNING_DELETE_TIME = 20           # Seconds before warning auto deletes

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# ==================================================
# FORCE JOIN CHECK
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

            # Build text with plain name
            safe_name = user.full_name or "User"

            text = (
                f"{safe_name} to be accepted in the group, "
                f"please subscribe to our channel.\n\n"
                f"Once joined, click the button below.\n\n"
                f"Action: Muted 🔇"
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
                entities=[
                    MessageEntity(
                        type="text_mention",
                        offset=0,
                        length=len(safe_name),
                        user=user
                    )
                ],
                reply_markup=reply_markup
            )

            # Auto-delete warning after X seconds
            await asyncio.sleep(WARNING_DELETE_TIME)
            try:
                await warning.delete()
            except:
                pass

    except Exception as e:
        logger.error(f"Force join error: {e}")

# ==================================================
# VERIFY BUTTON
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
                "✅ Verification Successful!\n\n"
                "You can now send messages in this group."
            )

        else:
            await query.answer(
                "❌ Please join the channel first.",
                show_alert=True
            )

    except Exception as e:
        logger.error(f"Verification error: {e}")

# ==================================================
# MAIN
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

    logger.info("🚀 Force Join Bot Running...")
    app.run_polling()

# ==================================================
# ENTRY POINT
# ==================================================

if __name__ == "__main__":
    main()

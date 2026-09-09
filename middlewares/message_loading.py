"""Instant feedback for message-based menu buttons.

Reply-keyboard buttons are Message updates, so Telegram has no callback
spinner. We send a lightweight typing action before the real handler runs.
"""

from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.enums import ChatAction
from aiogram.types import Message


MENU_PREFIXES = (
    "/",
    "📤", "📥", "👤", "💎", "❓", "📊", "➕", "📢",
    "🛒", "🔍", "⭐", "💰", "💸", "❤️", "👎",
    "📄", "📦", "⚙️", "🛠",
)


class MessageLoadingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            text = (event.text or event.caption or "").strip()

            if text and text.startswith(MENU_PREFIXES):
                try:
                    await event.bot.send_chat_action(
                        chat_id=event.chat.id,
                        action=ChatAction.TYPING,
                    )
                except Exception:
                    # Loading feedback must never break the real handler.
                    pass

        return await handler(event, data)

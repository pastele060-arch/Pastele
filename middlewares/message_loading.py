"""Instant feedback for message-based menu buttons.

Reply-keyboard buttons are Message updates, so Telegram has no native
callback spinner. We send a lightweight typing action immediately before
the real handler runs.
"""
from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.enums import ChatAction


MENU_PREFIXES = (
    "/",
    "📤", "📥", "👤", "💎", "❓", "📊", "➕", "📢", "🛒", "🔍",
    "⭐", "💰", "💸", "❤️", "👎", "📄", "📦", "⚙️", "🛠",
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
                    # Loading feedback must never stop the actual handler.
                    pass

        return await handler(event, data)

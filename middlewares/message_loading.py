"""Instant feedback for message-based menu buttons.

Reply-keyboard buttons are Message updates, so Telegram has no callback
spinner. We send a typing action immediately before the real handler runs.
This middleware is intentionally lightweight and never blocks the handler.
"""
from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatAction


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
                    pass
        return await handler(event, data)

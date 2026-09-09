"""Global immediate loading feedback for every inline callback.

The middleware ACKs callback queries before expensive handler/database work.
This gives Telegram's native button spinner immediate feedback and prevents
the UI from looking frozen. It deliberately never raises if the ACK fails.
"""
from __future__ import annotations

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery


def loading_text(data: str | None) -> str:
    value = (data or "").lower()

    if value.startswith(("lang", "language")):
        return "⏳ Menyiapkan bahasa..."
    if value.startswith(("open", "page", "all", "sendall", "next", "prev")):
        return "⏳ Memuat media..."
    if value.startswith(("pay", "premium", "cashi", "bayargg", "payment", "qr")):
        return "⏳ Memproses pembayaran..."
    if value.startswith(("like", "dislike", "favorite", "fav", "rating", "rate", "review")):
        return "⏳ Menyimpan pilihan..."
    if value.startswith(("market", "top", "category", "search")):
        return "⏳ Memuat marketplace..."
    if value.startswith(("account", "creator", "withdraw", "ewallet", "settings", "vip")):
        return "⏳ Memuat akun..."
    if value.startswith(("upfile", "getfile", "done", "cancel")):
        return "⏳ Menyiapkan file..."
    if value.startswith(("admin", "user_", "file_", "broadcast", "safety")):
        return "⏳ Memuat panel admin..."
    return "⏳ Memproses..."


class CallbackLoadingMiddleware(BaseMiddleware):
    """ACK every callback immediately so Telegram shows its native spinner."""

    async def __call__(self, handler, event, data):
        if isinstance(event, CallbackQuery):
            try:
                await event.answer(
                    loading_text(event.data),
                    show_alert=False,
                    cache_time=0,
                )
            except Exception:
                # UX feedback must never break the real handler.
                pass

        return await handler(event, data)

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from database import get_pool

router = Router()


def open_keyboard(code: str, lang: str = "id"):
    labels = {
        "id": ("📂 Open Page", "📤 Open All"),
        "en": ("📂 Open Page", "📤 Open All"),
        "zh": ("📂 打开页面", "📤 全部打开"),
    }
    a, b = labels.get(lang, labels["id"])

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=a, callback_data=f"page:{code}:1")],
            [InlineKeyboardButton(text=b, callback_data=f"all:{code}")],
        ]
    )


@router.callback_query(F.data.startswith("open:"))
async def open_code_callback(call: CallbackQuery):
    code = call.data.split(":", 1)[1]

    pool = await get_pool()
    exists = await pool.fetchval(
        "SELECT EXISTS(SELECT 1 FROM files WHERE lower(code)=lower($1))",
        code,
    )
    if not exists:
        await call.answer("❌ Code tidak ditemukan.", show_alert=True)
        return

    try:
        lang = (
            await pool.fetchval(
                "SELECT language FROM users WHERE user_id=$1",
                call.from_user.id,
            )
            or "id"
        )
    except Exception:
        lang = "id"

    await call.message.edit_text(
        "📂 <b>OPEN MENU</b>\n\nPilih cara membuka media:",
        parse_mode="HTML",
        reply_markup=open_keyboard(code, lang),
    )
    await call.answer()


@router.callback_query(F.data.startswith("all:"))
async def all_callback(call: CallbackQuery):
    code = call.data.split(":", 1)[1]

    from handlers.sendall import send_all
    await call.answer("📤 Memulai pengiriman...")
    await send_all(call.message, code)

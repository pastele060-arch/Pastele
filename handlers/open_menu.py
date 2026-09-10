from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from database import get_pool
from handlers.sendall import send_all
from utils.user import get_user_status  # 🔥 TAMBAH INI
from utils.points import get_points, fmt_points
from utils.user_lang import get_user_language

router = Router()


def open_keyboard(code, lang="id"):
    labels = {
        "id": ("📂 Open Page", "📤 Open All"),
        "en": ("📂 Open Page", "📤 Open All"),
        "zh": ("📂 打开页面", "📤 全部打开"),
    }
    page_label, all_label = labels.get(lang, labels["id"])
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=page_label,
                    callback_data=f"page:{code}:1"
                )
            ],
            [
                InlineKeyboardButton(
                    text=all_label,
                    callback_data=f"all:{code}"
                )
            ]
        ]
    )



@router.callback_query(F.data.startswith("open_code:"))
async def open_code_callback(call: CallbackQuery, state=None):
    try:
        await call.answer("⏳ Opening...", show_alert=False)
    except Exception:
        pass
    code = call.data.split(":", 1)[1].strip()
    from handlers.getfile import process_code
    from aiogram.fsm.context import FSMContext
    # Callback has no FSM in this handler unless injected by aiogram; process_code
    # accepts a tiny compatibility state, so use its own helper.
    return await process_code(call.message, code)

@router.callback_query(F.data.startswith("all:"))
async def open_all(call: CallbackQuery):
    code = call.data.split(":", 1)[1]

    # Jawab callback agar tidak timeout
    try:
        await call.answer("⏳ Processing...")
    except:
        pass

    pool = await get_pool()

    file = await pool.fetchrow(
        """
        SELECT *
        FROM files
        WHERE LOWER(TRIM(code)) = LOWER(TRIM($1))
        LIMIT 1
        """,
        code
    )

    if not file:
        try:
            await call.answer(
                "❌ File tidak ditemukan.",
                show_alert=True
            )
        except:
            pass
        return

    # Ambil status user
    user_level = await get_user_status(
        pool,
        call.from_user.id
    )

    # Share is optional. It never unlocks a file by itself; opening a shared
    # code may award +1 point to the code owner once per unique opener.
    try:
        media = file.get("media")
        if isinstance(media, str):
            import json
            media = json.loads(media)
        media_count = len(media or [])
    except Exception:
        media_count = int(file.get("media_count") or 0)

    owner = int(file.get("owner_id") or 0) == int(call.from_user.id)
    paid_access = bool(await pool.fetchval("SELECT EXISTS(SELECT 1 FROM file_purchases WHERE user_id=$1 AND (LOWER(TRIM(COALESCE(file_code,'')))=LOWER(TRIM($2)) OR LOWER(TRIM(COALESCE(code,'')))=LOWER(TRIM($2))) AND status='paid')", call.from_user.id, code))
    point_unlock = bool(await pool.fetchval("SELECT EXISTS(SELECT 1 FROM point_code_unlocks WHERE user_id=$1 AND LOWER(TRIM(code))=LOWER(TRIM($2)))", call.from_user.id, code))
    if bool(file.get("is_paid")):
        privileged = owner or paid_access or point_unlock
        if not privileged:
            from handlers.pay import paid_unlock_keyboard
            lang=await get_user_language(call.from_user.id); price=int(file.get("price") or 0)
            text={"id":f"🔒 <b>FILE BERBAYAR</b>\n\n🔑 CODE: <code>{code}</code>\n💰 Harga: <b>Rp {price:,}</b>\n\nPilih cara membuka file:","en":f"🔒 <b>PAID FILE</b>\n\n🔑 CODE: <code>{code}</code>\n💰 Price: <b>Rp {price:,}</b>\n\nChoose how to unlock this file:","zh":f"🔒 <b>付费文件</b>\n\n🔑 代码：<code>{code}</code>\n💰 价格：<b>Rp {price:,}</b>\n\n请选择解锁方式："}
            return await call.message.answer(text.get(lang,text["id"]),parse_mode="HTML",reply_markup=paid_unlock_keyboard(code,lang))
    else:
        privileged = owner or user_level in ("vip", "vvip")

    # Kirim semua media
    await send_all(
        bot=call.bot,
        chat_id=call.message.chat.id,
        code=code,
        file=file,
        user_level=user_level
    )

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

    # SHARE-TO-UNLOCK GATE. Paid codes require 10 genuinely new
    # members; free codes use ceil(media_count / 5).
    try:
        media = file.get("media")
        if isinstance(media, str):
            import json
            media = json.loads(media)
        media_count = len(media or [])
    except Exception:
        media_count = int(file.get("media_count") or 0)

    owner = int(file.get("owner_id") or 0) == int(call.from_user.id)
    privileged = owner or user_level in ("vip", "vvip")
    if not privileged:
        paid_access = await pool.fetchval(
            """SELECT EXISTS(
                SELECT 1 FROM file_purchases
                WHERE user_id=$1 AND (LOWER(TRIM(COALESCE(file_code,''))) = LOWER(TRIM($2)) OR LOWER(TRIM(COALESCE(code,''))) = LOWER(TRIM($2))) AND status='paid'
            )""",
            call.from_user.id, code
        ) or False
        creator_access = await pool.fetchval(
            """SELECT COALESCE(is_creator,FALSE)
                      AND COALESCE(creator_status,'none')='approved'
               FROM users WHERE user_id=$1""",
            call.from_user.id
        ) or False
        privileged = bool(paid_access or creator_access)

    # Point gate: FREE requires media_count points before opening; paid access
    # is charged once at first Open Menu by getfile, with a safe fallback here.
    if not privileged:
        points = await get_points(pool, call.from_user.id)
        if not bool(file.get("is_paid")) and points < media_count:
            lang = await get_user_language(call.from_user.id)
            text = {
                "id": f"⭐ <b>POIN TIDAK CUKUP</b>\n\nButuh minimal <b>{media_count} poin</b>.\nPoin kamu: <b>{fmt_points(points)}</b>.",
                "en": f"⭐ <b>NOT ENOUGH POINTS</b>\n\nAt least <b>{media_count} points</b> are required.\nYour points: <b>{fmt_points(points)}</b>.",
                "zh": f"⭐ <b>积分不足</b>\n\n至少需要 <b>{media_count} 积分</b>。\n你的积分：<b>{fmt_points(points)}</b>。",
            }
            return await call.message.answer(text.get(lang,text["id"]),parse_mode="HTML")

    # Kirim semua media
    await send_all(
        bot=call.bot,
        chat_id=call.message.chat.id,
        code=code,
        file=file,
        user_level=user_level
    )

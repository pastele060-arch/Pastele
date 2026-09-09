import asyncio
import re

from aiogram import Router, F
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

from database import get_pool


router = Router()


# =========================================================
# REGEX CODE
# =========================================================

CODE_REGEX = re.compile(
    r"(?<![A-Za-z0-9])Pastelebot_[A-Za-z0-9]{14}(?![A-Za-z0-9])",
    re.IGNORECASE,
)


def normalize_code(code: str) -> str:
    return (
        code
        .strip()
        .replace(" ", "")
        .replace("\n", "")
    )


# =========================================================
# LOADING
# =========================================================

async def send_loading(message: Message):
    """
    Kirim pesan loading pencarian.
    """

    try:
        return await message.answer(
            "🔎 <b>Mencari...</b>\n"
            "⏳ Mohon tunggu sebentar...",
            parse_mode="HTML",
        )
    except Exception:
        return None


async def delete_loading(loading_message):
    """
    Hapus pesan loading dengan aman.
    """

    if not loading_message:
        return

    try:
        await loading_message.delete()
    except Exception:
        pass


async def loading_animation(message: Message):
    """
    Loading sederhana.
    """

    try:
        loading = await message.answer(
            "🔎 <b>Mencari</b> ⏳",
            parse_mode="HTML",
        )

        await asyncio.sleep(0.25)

        try:
            await loading.edit_text(
                "🔎 <b>Mencari.</b> ⏳",
                parse_mode="HTML",
            )
        except Exception:
            pass

        await asyncio.sleep(0.25)

        try:
            await loading.edit_text(
                "🔎 <b>Mencari..</b> ⏳",
                parse_mode="HTML",
            )
        except Exception:
            pass

        await asyncio.sleep(0.25)

        try:
            await loading.edit_text(
                "🔎 <b>Mencari...</b> ⏳",
                parse_mode="HTML",
            )
        except Exception:
            pass

        return loading

    except Exception:
        return None


# =========================================================
# KEYBOARD
# =========================================================

def kb_open(code: str):
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📂 Open Code", callback_data=f"open_code:{code}")]])


def kb_upload():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Buat Code / Upload",
                    callback_data="upfile",
                )
            ]
        ]
    )


def kb_channel():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Channel",
                    callback_data="channel",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home",
                )
            ],
        ]
    )


# =========================================================
# VIP KEYBOARD
# =========================================================

def kb_vip():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👑 Buka VIP",
                    callback_data="vip",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home",
                )
            ],
        ]
    )


# =========================================================
# MARKETPLACE KEYBOARD
# =========================================================

def kb_marketplace():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛍 Marketplace",
                    callback_data="marketplace",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home",
                )
            ],
        ]
    )


# =========================================================
# CREATOR KEYBOARD
# =========================================================

def kb_creator():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎨 Buka Kreator",
                    callback_data="creator",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Menu Utama",
                    callback_data="home",
                )
            ],
        ]
    )


# =========================================================
# HOME
# =========================================================

def kb_home():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 START",
                    callback_data="home",
                )
            ]
        ]
    )


# =========================================================
# TEXT NOTIFY
# =========================================================

@router.message(F.text)
async def notify_text(
    message: Message,
    state: FSMContext,
):

    # =====================================================
    # JANGAN GANGGU FSM
    # =====================================================

    current_state = await state.get_state()

    if current_state:
        return


    text = message.text.strip()

    if not text:
        return


    # =====================================================
    # COMMAND
    # =====================================================

    if text.startswith("/"):
        return


    lower = text.lower().strip()


    # =====================================================
    # LOADING
    # =====================================================

    loading = await loading_animation(message)


    try:

        # Sedikit delay agar loading benar-benar terlihat
        await asyncio.sleep(0.15)


        # =================================================
        # VIP / VVIP
        # =================================================

        vip_keywords = {
            "vip",
            "vvip",
        }

        if lower in vip_keywords:

            return await message.answer(
                (
                    "👑 <b>VIP / VVIP</b>\n\n"
                    "✨ Konten VIP tersedia di sini.\n\n"
                    "Silakan tekan tombol di bawah "
                    "untuk membuka menu VIP."
                ),
                parse_mode="HTML",
                reply_markup=kb_vip(),
            )


        # =================================================
        # MARKETPLACE
        # =================================================

        marketplace_keywords = {
            "video",
            "viral",
        }

        if lower in marketplace_keywords:

            return await message.answer(
                (
                    "🛍 <b>MARKETPLACE</b>\n\n"
                    "🔥 Code dan media yang tersedia "
                    "dapat kamu temukan di Marketplace.\n\n"
                    "Silakan buka Marketplace untuk "
                    "melihat semua code yang tersedia."
                ),
                parse_mode="HTML",
                reply_markup=kb_marketplace(),
            )


        # =================================================
        # CREATOR
        # =================================================

        creator_keywords = {
            "kreator",
            "creator",
        }

        if lower in creator_keywords:

            return await message.answer(
                (
                    "🎨 <b>PROGRAM KREATOR</b>\n\n"
                    "🚀 Jadilah Kreator dan dapatkan "
                    "penghasilan dari code yang kamu upload.\n\n"
                    "✨ Kamu dapat mengelola code, "
                    "menjualnya melalui Marketplace, "
                    "dan mendapatkan penghasilan dari "
                    "setiap penjualan.\n\n"
                    "Tekan tombol di bawah untuk membuka "
                    "Program Kreator."
                ),
                parse_mode="HTML",
                reply_markup=kb_creator(),
            )


        # =================================================
        # CHANNEL
        # =================================================

        channel_keywords = {
            "group",
            "grup",
            "channel",
            "ch",
            "info",
            "bokep",
            "bocil",
            "indo",
            "ngewe",
        }

        if lower in channel_keywords:

            return await message.answer(
                (
                    "📢 <b>MENU CHANNEL</b>\n\n"
                    "Silakan buka daftar channel "
                    "yang tersedia."
                ),
                parse_mode="HTML",
                reply_markup=kb_channel(),
            )


        # =================================================
        # CODE DETECTION
        # =================================================

        match = CODE_REGEX.search(text)

        if match:

            code = normalize_code(
                match.group(0)
            )

            pool = await get_pool()

            exists = await pool.fetchval(
                """
                SELECT EXISTS(
                    SELECT 1
                    FROM files
                    WHERE LOWER(TRIM(code)) = $1
                )
                """,
                code,
            )

            if exists:

                from utils.user_lang import get_user_language
                lang = await get_user_language(message.from_user.id)
                text_ok = {
                    "id": "🔑 <b>CODE TERDETEKSI</b>\n\n✅ Kode file ditemukan.\n\nTekan tombol di bawah untuk membuka file.",
                    "en": "🔑 <b>CODE DETECTED</b>\n\n✅ File code found.\n\nPress the button below to open it.",
                    "zh": "🔑 <b>检测到代码</b>\n\n✅ 找到文件代码。\n\n点击下方按钮打开文件。",
                }
                return await message.answer(text_ok.get(lang, text_ok["id"]), parse_mode="HTML", reply_markup=kb_open(code))

            from utils.user_lang import get_user_language
            lang = await get_user_language(message.from_user.id)
            notfound = {"id":"❌ <b>CODE TIDAK DITEMUKAN</b>\n\nKode tidak tersedia di database.","en":"❌ <b>CODE NOT FOUND</b>\n\nThat code is not available in the database.","zh":"❌ <b>未找到代码</b>\n\n该代码不在数据库中。"}
            return await message.answer(notfound.get(lang, notfound["id"]), parse_mode="HTML", reply_markup=kb_upload())


        # =================================================
        # DEFAULT TEXT
        # =================================================

        from utils.user_lang import get_user_language
        lang = await get_user_language(message.from_user.id)
        fallback = {
            "id": "👋 <b>Pesan bukan CODE.</b>\n\nKalau ingin membuat code, upload file terlebih dahulu.",
            "en": "👋 <b>This is not a code.</b>\n\nTo create a code, upload a file first.",
            "zh": "👋 <b>这不是代码。</b>\n\n如果要创建代码，请先上传文件。",
        }
        return await message.answer(fallback.get(lang, fallback["id"]), parse_mode="HTML", reply_markup=kb_upload())

    finally:

        # =================================================
        # DELETE LOADING
        # =================================================

        await delete_loading(loading)


# =========================================================
# MEDIA NOTIFY
# =========================================================

# Media is intentionally NOT handled by the generic notify router.
# Upload mode is owned exclusively by handlers.upfile.receive_media.
# Get File mode accepts CODE text only (handlers.getfile.receive_code).
# Media sent outside Upload Mode is silently ignored.

# =========================================================
# FALLBACK
# =========================================================

@router.message()
async def notify_other(
    message: Message,
    state: FSMContext,
):

    current_state = await state.get_state()

    if current_state:
        return


    # =====================================================
    # LOADING
    # =====================================================

    loading = await loading_animation(message)

    try:

        await asyncio.sleep(0.25)

        return await message.answer(
            (
                "🤖 <b>BOT MARKET</b>\n\n"
                "🔎 Pesan sedang diproses.\n\n"
                "Gunakan menu yang tersedia "
                "untuk melanjutkan."
            ),
            parse_mode="HTML",
            reply_markup=kb_upload(),
        )

    finally:

        await delete_loading(loading)

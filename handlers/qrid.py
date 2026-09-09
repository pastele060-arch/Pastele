from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_pool
from handlers.admin.admins import is_admin
from utils.user_lang import get_user_language

router = Router()

class QRIDState(StatesGroup):
    waiting_qr = State()

@router.message(F.text == "/qrid")
async def qrid_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Kamu bukan admin.")
    lang = await get_user_language(message.from_user.id)
    prompt = {
        "id": "📷 <b>Kirim QR Manual sekarang.</b>\n\nKirim foto QR di chat ini. Bot akan menyimpan Chat ID dan Message ID secara otomatis.",
        "en": "📷 <b>Send the manual QR now.</b>\n\nSend the QR image in this chat. The bot will save the Chat ID and Message ID automatically.",
        "zh": "📷 <b>请现在发送手动二维码。</b>\n\n请在此聊天中发送二维码图片。机器人会自动保存聊天 ID 和消息 ID。",
    }.get(lang, "📷 <b>Kirim QR Manual sekarang.</b>\n\nKirim foto QR di chat ini.")
    await state.set_state(QRIDState.waiting_qr)
    await message.answer(prompt, parse_mode="HTML")

@router.message(QRIDState.waiting_qr)
async def qrid_receive(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    if not (message.photo or message.document):
        return await message.answer("❌ Kirim QR sebagai foto atau gambar.")
    pool = await get_pool()
    await pool.execute("INSERT INTO settings(key,value) VALUES($1,$2) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value", "manual_qr_chat_id", str(message.chat.id))
    await pool.execute("INSERT INTO settings(key,value) VALUES($1,$2) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value", "manual_qr_message_id", str(message.message_id))
    await pool.execute("INSERT INTO settings(key,value) VALUES($1,$2) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value", "manual_qr_configured", "on")
    if message.photo:
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id
    await pool.execute("INSERT INTO settings(key,value) VALUES($1,$2) ON CONFLICT(key) DO UPDATE SET value=EXCLUDED.value", "manual_qr_file_id", file_id)
    await state.clear()
    lang = await get_user_language(message.from_user.id)
    text = {
        "id": (
            "✅ <b>QR Manual tersimpan.</b>\n\n"
            f"🆔 Chat ID: <code>{message.chat.id}</code>\n"
            f"🆔 Message ID: <code>{message.message_id}</code>\n\n"
            "QR ini sekarang siap digunakan dari metode QR Manual."
        ),
        "en": (
            "✅ <b>Manual QR saved.</b>\n\n"
            f"🆔 Chat ID: <code>{message.chat.id}</code>\n"
            f"🆔 Message ID: <code>{message.message_id}</code>\n\n"
            "This QR is now ready for the Manual QR payment method."
        ),
        "zh": (
            "✅ <b>手动二维码已保存。</b>\n\n"
            f"🆔 聊天 ID：<code>{message.chat.id}</code>\n"
            f"🆔 消息 ID：<code>{message.message_id}</code>\n\n"
            "现在可以通过手动二维码支付方式使用。"
        ),
    }.get(lang, "QR Manual tersimpan.")
    await message.answer(text, parse_mode="HTML")

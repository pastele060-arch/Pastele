from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_pool
from handlers.admin.admins import is_admin

router = Router()

class QRIDState(StatesGroup):
    waiting_qr = State()

@router.message(F.text == "/qrid")
async def qrid_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return await message.answer("❌ Kamu bukan admin.")
    await state.set_state(QRIDState.waiting_qr)
    await message.answer(
        "📷 <b>Kirim QR Manual sekarang.</b>\n\n"
        "Kirim sebagai foto atau dokumen gambar. Setelah diterima, bot akan memberikan <b>Chat ID + Message ID</b> yang bisa dipasang di pengaturan pembayaran.",
        parse_mode="HTML",
    )

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
    await message.answer(
        "✅ <b>QR Manual tersimpan.</b>\n\n"
        f"🆔 Chat ID: <code>{message.chat.id}</code>\n"
        f"🆔 Message ID: <code>{message.message_id}</code>\n\n"
        "Gunakan kedua ID tersebut pada pengaturan QR Manual."
        , parse_mode="HTML"
    )

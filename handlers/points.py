from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from database import get_pool
from utils.points import get_points, checkin, fmt_points
from utils.cashi import Cashi


router = Router()
logger = logging.getLogger(__name__)


# ============================================================
# POINT PACKAGES
#
# Harga:
# Rp 2.000  -> 20 poin
# Rp 5.000  -> 100 poin
# Rp 10.000 -> 200 poin
# Rp 20.000 -> 400 poin
# Rp 50.000 -> 1.000 poin
#
# Format:
# (JUMLAH_POIN, HARGA_RUPIAH)
# ============================================================

PACKAGES = [
    (20, 2_000),
    (100, 5_000),
    (200, 10_000),
    (400, 20_000),
    (1_000, 50_000),
]


# ============================================================
# POINT MENU KEYBOARD
# ============================================================

def menu_kb(lang: str) -> InlineKeyboardMarkup:
    labels = {
        "id": (
            "📅 Cek In Harian",
            "💳 Buy Poin",
            "📖 Kegunaan Poin",
            "⬅️ Kembali",
        ),
        "en": (
            "📅 Daily Check-in",
            "💳 Buy Points",
            "📖 How Points Work",
            "⬅️ Back",
        ),
        "zh": (
            "📅 每日签到",
            "💳 购买积分",
            "📖 积分说明",
            "⬅️ 返回",
        ),
    }

    a, b, c, d = labels.get(lang, labels["id"])

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=a,
                    callback_data="points_checkin",
                )
            ],
            [
                InlineKeyboardButton(
                    text=b,
                    callback_data="points_buy",
                )
            ],
            [
                InlineKeyboardButton(
                    text=c,
                    callback_data="points_info",
                )
            ],
            [
                InlineKeyboardButton(
                    text=d,
                    callback_data="home",
                )
            ],
        ]
    )


# ============================================================
# GET USER LANGUAGE
# ============================================================

async def lang(uid: int) -> str:
    pool = await get_pool()

    language = await pool.fetchval(
        """
        SELECT language
        FROM users
        WHERE user_id = $1
        """,
        uid,
    )

    return language or "id"


# ============================================================
# POINTS MAIN PAGE
# ============================================================

async def render(call: CallbackQuery):
    uid = call.from_user.id

    language = await lang(uid)

    pool = await get_pool()
    pts = await get_points(pool, uid)

    texts = {
        "id": (
            "⭐ <b>POIN KAMU</b>\n\n"
            f"Total Poin: <b>{fmt_points(pts)}</b>\n\n"
            "Poin dipakai untuk membuka code dan mengirim media.\n\n"
            "📅 Cek In • dapat poin harian\n"
            "📤 Upload • 50 media = +10 poin, 100 media = +20 poin\n"
            "📤 Share • tidak dapat poin langsung\n"
            "👤 Orang membuka code yang kamu share • +1 poin\n"
            "📦 Buka media FREE • 1.20 poin/media\n"
            "💰 Code PAID • butuh poin sebesar harga code."
        ),

        "en": (
            "⭐ <b>YOUR POINTS</b>\n\n"
            f"Total Points: <b>{fmt_points(pts)}</b>\n\n"
            "Points are used to open codes and deliver media.\n\n"
            "📅 Check-in • daily points\n"
            "📤 Upload • 50 media = +10 points, 100 media = +20 points\n"
            "📤 Share • no direct reward\n"
            "👤 Someone opens your shared code • +1 point\n"
            "📦 FREE media • 1.20 points/media\n"
            "💰 PAID code • requires points equal to its price."
        ),

        "zh": (
            "⭐ <b>你的积分</b>\n\n"
            f"总积分：<b>{fmt_points(pts)}</b>\n\n"
            "积分用于打开代码和发送媒体。\n\n"
            "📅 签到 • 每日获得积分\n"
            "📤 上传 • 50 个媒体 = +10 积分，100 个媒体 = +20 积分\n"
            "📤 分享 • 分享本身不奖励\n"
            "👤 他人打开你分享的代码 • +1 积分\n"
            "📦 免费媒体 • 每个媒体消耗 1.20 积分\n"
            "💰 付费代码 • 需要等于代码价格的积分。"
        ),
    }

    await call.message.edit_text(
        texts.get(language, texts["id"]),
        parse_mode="HTML",
        reply_markup=menu_kb(language),
    )

    await call.answer()


# ============================================================
# OPEN POINTS MENU
# ============================================================

@router.callback_query(F.data == "points")
async def points_menu(call: CallbackQuery):
    await render(call)


# ============================================================
# POINT INFORMATION
# ============================================================

@router.callback_query(F.data == "points_info")
async def points_info(call: CallbackQuery):
    await render(call)


# ============================================================
# DAILY CHECK-IN
# ============================================================

@router.callback_query(F.data == "points_checkin")
async def points_checkin(call: CallbackQuery):
    await call.answer("⏳")

    uid = call.from_user.id
    pool = await get_pool()

    result, status = await checkin(pool, uid)

    language = await lang(uid)

    if status == "already":

        messages = {
            "id": "⚠️ Kamu sudah check-in hari ini.",
            "en": "⚠️ You already checked in today.",
            "zh": "⚠️ 今天已经签到。",
        }

        msg = messages.get(
            language,
            messages["id"],
        )

    elif status == "user_not_found":

        messages = {
            "id": "❌ User tidak ditemukan.",
            "en": "❌ User not found.",
            "zh": "❌ 未找到用户。",
        }

        msg = messages.get(
            language,
            messages["id"],
        )

    else:

        day = int(status)

        rewards = [
            "0.5",
            "1",
            "1",
            "1",
            "1.5",
            "2",
            "3",
        ]

        reward = rewards[day - 1]

        messages = {
            "id": (
                "✅ <b>Check-in berhasil!</b>\n\n"
                f"Hari ke-{day}: <b>+{reward} poin</b>\n"
                f"Total: <b>{fmt_points(result)}</b>"
            ),

            "en": (
                "✅ <b>Check-in complete!</b>\n\n"
                f"Day {day}: <b>+{reward} points</b>\n"
                f"Total: <b>{fmt_points(result)}</b>"
            ),

            "zh": (
                "✅ <b>签到成功！</b>\n\n"
                f"第 {day} 天：<b>+{reward} 积分</b>\n"
                f"总计：<b>{fmt_points(result)}</b>"
            ),
        }

        msg = messages.get(
            language,
            messages["id"],
        )

    await call.message.edit_text(
        msg,
        parse_mode="HTML",
        reply_markup=menu_kb(language),
    )


# ============================================================
# BUY POINTS PAGE
# ============================================================

@router.callback_query(F.data == "points_buy")
async def points_buy(call: CallbackQuery):

    language = await lang(
        call.from_user.id
    )

    title = {
        "id": "💳 <b>BUY POIN</b>",
        "en": "💳 <b>BUY POINTS</b>",
        "zh": "💳 <b>购买积分</b>",
    }[language]

    desc = {
        "id": "Pilih paket poin yang kamu butuhkan.",
        "en": "Choose the points package you need.",
        "zh": "选择需要的积分套餐。",
    }[language]

    one = {
        "id": "1 poin = Rp1",
        "en": "1 point = Rp1",
        "zh": "1 积分 = Rp1",
    }[language]

    back = {
        "id": "⬅️ Kembali",
        "en": "⬅️ Back",
        "zh": "⬅️ 返回",
    }[language]

    unit = {
        "id": "Poin",
        "en": "Points",
        "zh": "积分",
    }[language]

    rows = []

    for points, amount in PACKAGES:

        price = f"Rp {amount:,}".replace(
            ",",
            ".",
        )

        point_display = f"{points:,}".replace(
            ",",
            ".",
        )

        rows.append(
            [
                InlineKeyboardButton(
                    text=(
                        f"⭐ {point_display} "
                        f"{unit} • {price}"
                    ),
                    callback_data=(
                        f"points_pkg:{points}"
                    ),
                )
            ]
        )

    rows.append(
        [
            InlineKeyboardButton(
                text=back,
                callback_data="points",
            )
        ]
    )

    await call.message.edit_text(
        f"{title}\n\n"
        f"{desc}\n\n"
        f"<b>{one}</b>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=rows
        ),
    )

    await call.answer()


# ============================================================
# SELECT POINT PACKAGE
# ============================================================

@router.callback_query(
    F.data.startswith("points_pkg:")
)
async def points_pkg(call: CallbackQuery):

    try:
        points = int(
            call.data.split(
                ":",
                1,
            )[1]
        )

    except (
        ValueError,
        IndexError,
    ):
        return await call.answer(
            "❌ Invalid package.",
            show_alert=True,
        )

    valid_packages = dict(PACKAGES)

    if points not in valid_packages:
        return await call.answer(
            "❌ Paket tidak valid.",
            show_alert=True,
        )

    # Semua pembelian poin masuk
    # ke payment flow utama.
    from handlers.pay import (
        create_points_payment,
    )

    return await create_points_payment(
        call,
        points,
    )


# ============================================================
# SETTLE POINT ORDER
# ============================================================

async def settle(order_id: str):

    pool = await get_pool()

    async with pool.acquire() as conn:

        async with conn.transaction():

            row = await conn.fetchrow(
                """
                SELECT *
                FROM point_orders
                WHERE order_id = $1
                FOR UPDATE
                """,
                order_id,
            )

            if not row:
                return False

            current_status = str(
                row["status"] or ""
            ).lower()

            if current_status == "paid":
                return True

            await conn.execute(
                """
                UPDATE point_orders
                SET
                    status = 'paid',
                    paid_at = NOW(),
                    updated_at = NOW()
                WHERE id = $1
                """,
                row["id"],
            )

            ref = (
                f'points_purchase:{row["id"]}'
            )

            balance = await conn.fetchval(
                """
                SELECT points
                FROM users
                WHERE user_id = $1
                FOR UPDATE
                """,
                row["user_id"],
            )

            if balance is None:
                logger.error(
                    "User %s tidak ditemukan "
                    "saat settle point order %s",
                    row["user_id"],
                    order_id,
                )
                return False

            new_balance = (
                balance + row["points"]
            )

            await conn.execute(
                """
                UPDATE users
                SET
                    points = $1,
                    updated_at = NOW()
                WHERE user_id = $2
                """,
                new_balance,
                row["user_id"],
            )

            await conn.execute(
                """
                INSERT INTO point_transactions(
                    user_id,
                    amount,
                    balance_after,
                    type,
                    reference,
                    description
                )
                VALUES(
                    $1,
                    $2,
                    $3,
                    'purchase',
                    $4,
                    $5
                )
                ON CONFLICT(reference)
                DO NOTHING
                """,
                row["user_id"],
                row["points"],
                new_balance,
                ref,
                f'Buy {row["points"]} points',
            )

            return True


# ============================================================
# CHECK POINT PAYMENT
#
# Routed centrally through handlers.pay
# ============================================================

async def points_check(call: CallbackQuery):

    await call.answer(
        "⏳ Mengecek..."
    )

    try:
        order = call.data.split(
            ":",
            1,
        )[1]
    except (
        ValueError,
        IndexError,
    ):
        return await call.answer(
            "❌ Order tidak valid.",
            show_alert=True,
        )

    uid = call.from_user.id

    pool = await get_pool()

    row = await pool.fetchrow(
        """
        SELECT *
        FROM point_orders
        WHERE order_id = $1
          AND user_id = $2
        """,
        order,
        uid,
    )

    if not row:
        return await call.message.answer(
            "❌ Order tidak ditemukan."
        )

    if str(
        row["status"] or ""
    ).lower() == "paid":

        pts = await get_points(
            pool,
            uid,
        )

        return await call.message.answer(
            "✅ <b>Poin sudah ditambahkan.</b>\n\n"
            f"⭐ Total: <b>{fmt_points(pts)}</b>",
            parse_mode="HTML",
        )

    # asyncpg.Record tidak perlu .get().
    # Cek nama kolom secara aman.
    try:
        provider_value = row["provider"]
    except (KeyError, TypeError):
        provider_value = None

    provider = str(
        provider_value or "cashi"
    ).lower()

    # ========================================================
    # BAYARGG
    # ========================================================

    if provider == "bayargg":

        from utils.bayargg import BayarGG

        result = await BayarGG.check_payment(
            order
        )

    # ========================================================
    # CASHI
    # ========================================================

    else:

        result = await Cashi.check_payment(
            order
        )

    status = str(
        (result or {}).get("status") or ""
    ).lower()

    success_statuses = {
        "paid",
        "success",
        "settled",
        "completed",
        "completed_payment",
        "success_payment",
        "settlement",
    }

    if status in success_statuses:

        success = await settle(
            order
        )

        if not success:
            return await call.message.answer(
                "❌ Gagal menambahkan poin. "
                "Silakan coba lagi."
            )

        pts = await get_points(
            pool,
            uid,
        )

        return await call.message.answer(
            "✅ <b>Pembayaran berhasil!</b>\n\n"
            f"⭐ +{fmt_points(row['points'])} poin\n"
            f"⭐ Total: <b>{fmt_points(pts)}</b>",
            parse_mode="HTML",
        )

    return await call.answer(
        "⏳ Belum terkonfirmasi.",
        show_alert=True,
    )

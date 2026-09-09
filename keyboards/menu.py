from __future__ import annotations
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
def _button(
    text: str,
    callback_data: str | None = None,
    url: str | None = None,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
        url=url,
    )
# ============================================================
# HOME
# ============================================================
def home_kb(
    user_id: int,
    lang: str = "id",
    is_creator: bool = False,
) -> InlineKeyboardMarkup:
    idn = lang == "id"
    zh = lang == "zh"
    return InlineKeyboardMarkup(inline_keyboard=[
        [_button("📤 Up File" if not zh else "📤 上传文件", callback_data="upfile"),
         _button("📥 Get File" if not zh else "📥 获取文件", callback_data="getfile")],
        [_button("🛍️ Marketplace" if not zh else "🛍️ 市场", callback_data="marketplace"),
         _button("👤 Akun" if idn else "👤 Account" if not zh else "👤 账户", callback_data="account")],
        [_button("💎 VIP / 🎨 Kreator" if idn else "💎 VIP / 🎨 Creator" if not zh else "💎 VIP / 🎨 创作者", callback_data="vip_creator"),
         _button("📂 Menu Lainnya" if idn else "📂 More Menu" if not zh else "📂 更多菜单", callback_data="menu_lainnya")],
    ])
# ============================================================
# ACCOUNT
# ============================================================
def account_kb(
    lang: str = "id",
    is_creator: bool = False,
) -> InlineKeyboardMarkup:
    idn = lang == "id"
    rows = [
        [
            _button(
                "⚙️ Pengaturan" if idn else "⚙️ Settings",
                callback_data="account_settings",
            )
        ],
        [
            _button(
                "🎨 Kreator" if idn else "🎨 Creator",
                callback_data="creator",
            ),
            _button(
                "💎 VIP",
                callback_data="vvip",
            ),
        ],
    ]
    if is_creator:
        rows.append(
            [
                _button(
                    "💸 Withdraw",
                    callback_data="withdraw",
                )
            ]
        )
    rows.append(
        [
            _button(
                "⬅️ Kembali" if idn else "⬅️ Back",
                callback_data="home",
            )
        ]
    )
    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )
# ============================================================
# SETTINGS
# ============================================================
def settings_kb(
    lang: str = "id",
) -> InlineKeyboardMarkup:
    idn = lang == "id"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                _button(
                    "💳 Setting Withdraw"
                    if idn
                    else "💳 Withdraw Settings",
                    callback_data="ewallet",
                )
            ],
            [
                _button(
                    "🌐 Bahasa" if idn else "🌐 Language",
                    callback_data="change_language",
                )
            ],
            [
                _button(
                    "⬅️ Account",
                    callback_data="account",
                )
            ],
        ]
    )
# ============================================================
# OTHER MENU
# ============================================================
def other_menu_kb(lang: str = "id") -> InlineKeyboardMarkup:
    idn = lang == "id"
    return InlineKeyboardMarkup(inline_keyboard=[
        [_button("📤 Share Code" if idn else "📤 Share Code", callback_data="share_code")],
        [_button("📦 Code Saya" if idn else "📦 My Code", callback_data="my_code")],
        [_button("🌐 Pilih Bahasa" if idn else "🌐 Language", callback_data="change_language")],
        [_button("🏦 Metode Bank" if idn else "🏦 Bank Method", callback_data="ewallet")],
        [_button("💸 Withdraw" if idn else "💸 Withdraw", callback_data="withdraw")],
        [_button("⭐ Channel Review" if idn else "⭐ Review Channel", callback_data="channel_review")],
        [_button("💳 Channel Transaksi" if idn else "💳 Transaction Channel", callback_data="channel_transaction")],
        [_button("🔔 Channel Notifikasi" if idn else "🔔 Notification Channel", callback_data="channel_notification")],
        [_button("❓ Help / Bantuan" if idn else "❓ Help", callback_data="help")],
        [_button("⬅️ Kembali" if idn else "⬅️ Back", callback_data="home")],
    ])

import asyncio
import io
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

import config
import database as db
import card_generator as cg
import bin_detector as bd
from health_server import start_health_server

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

config.BOT_START_TIME = time.time()

SEP = "━" * 30
COUNTRIES_PER_PAGE = 8
BANKS_PER_PAGE = 8
CUSTOM_BINS_PER_PAGE = 10


def is_admin(user_id: int) -> bool:
    return user_id == config.ADMIN_ID


def get_uptime() -> str:
    if not config.BOT_START_TIME:
        return "Unknown"
    elapsed = int(time.time() - config.BOT_START_TIME)
    days, rem = divmod(elapsed, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if mins:
        parts.append(f"{mins}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def authorized_check(user_id: int) -> bool:
    return db.is_user_active(user_id)


def progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total) if total else width
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * current / total) if total else 100
    return f"[{bar}] {pct}%"


def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton("💳 Generate Test Cards", callback_data="gen_start")],
        [
            InlineKeyboardButton("👤 My Profile", callback_data="profile"),
            InlineKeyboardButton("📊 Statistics", callback_data="stats"),
        ],
        [
            InlineKeyboardButton("ℹ️ About", callback_data="about"),
            InlineKeyboardButton("🆘 Help", callback_data="help"),
        ],
    ]
    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("🔐 Admin Panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(buttons)


def back_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]])


# ─── Commands ────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_or_update_user(user.id, user.username or "", user.first_name or "")
    if authorized_check(user.id):
        expiry = db.get_subscription_expiry(user.id)
        remaining = expiry - datetime.utcnow() if expiry else timedelta(0)
        h, rem = divmod(int(max(remaining.total_seconds(), 0)), 3600)
        m = rem // 60
        exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC") if expiry else "N/A"
        text = (
            f"╔══════════════════════════╗\n"
            f"║   🃏 CC GENERATOR BOT   ║\n"
            f"╚══════════════════════════╝\n\n"
            f"Welcome back, *{user.first_name}*! ✨\n\n"
            f"✅ *Subscription Active*\n"
            f"⏳ Expires: `{exp_str}`\n"
            f"🕐 Remaining: `{h}h {m}m`\n\n"
            f"Choose an option below:"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=main_menu_keyboard(user.id))
    else:
        text = (
            f"╔══════════════════════════╗\n"
            f"║   🃏 CC GENERATOR BOT   ║\n"
            f"╚══════════════════════════╝\n\n"
            f"👋 Hello, *{user.first_name}*!\n\n"
            f"🔒 *This is an exclusive bot.*\n"
            f"You are not an authorised user.\n\n"
            f"If you have a licence key, use:\n"
            f"`/redeem YOUR-KEY-HERE`\n\n"
            f"Contact the admin to get a licence key."
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_or_update_user(user.id, user.username or "", user.first_name or "")
    args = context.args
    if not args:
        await update.message.reply_text(
            "❌ Please provide your licence key.\n\nUsage: `/redeem XXXX-XXXX-XXXX-XXXX`",
            parse_mode=ParseMode.MARKDOWN)
        return
    key = args[0].strip().upper()
    success, result = db.redeem_license(key, user.id)
    if success:
        expiry = result
        exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC")
        text = (
            f"🎉 *Licence Redeemed Successfully!*\n\n"
            f"✅ Subscription is now active.\n"
            f"📅 Expires: `{exp_str}`\n\n"
            f"Use the bot to generate test cards now!"
        )
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=main_menu_keyboard(user.id))
    else:
        await update.message.reply_text(str(result), parse_mode=ParseMode.MARKDOWN)


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to access this.")
        return
    await show_admin_panel(update, context, via_message=True)


# ─── Admin Panel ─────────────────────────────────────────────────────────────

async def show_admin_panel(update, context, via_message=False):
    stats = db.get_stats()
    active = db.get_active_users_count()
    custom_bin_count = db.get_custom_bins_count()
    uptime = get_uptime()
    text = (
        f"🔐 *ADMIN PANEL*\n"
        f"{SEP}\n"
        f"🤖 *Uptime:* `{uptime}`\n"
        f"👥 *Total Users:* `{stats.get('total_users', 0)}`\n"
        f"✅ *Active Users:* `{active}`\n"
        f"🔑 *Licences Generated:* `{stats.get('total_licenses_generated', 0)}`\n"
        f"🎟 *Licences Redeemed:* `{stats.get('total_licenses_redeemed', 0)}`\n"
        f"💳 *Cards Generated:* `{stats.get('total_cc_generated', 0)}`\n"
        f"🗄️ *Custom BINs:* `{custom_bin_count}`\n"
        f"{SEP}"
    )
    buttons = [
        [InlineKeyboardButton("🔑 Generate Licences", callback_data="admin_gen_lic")],
        [InlineKeyboardButton("🗄️ Manage BINs", callback_data="admin_bin_menu")],
        [InlineKeyboardButton("👥 View Users", callback_data="admin_users_0")],
        [InlineKeyboardButton("🔑 View Licences", callback_data="admin_view_lic")],
        [InlineKeyboardButton("❌ Revoke User", callback_data="admin_revoke")],
        [InlineKeyboardButton("📣 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton("📊 Full Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_panel")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    markup = InlineKeyboardMarkup(buttons)
    if via_message:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)
    else:
        await update.callback_query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=markup)


async def show_bin_menu(query, context):
    custom_bin_count = db.get_custom_bins_count()
    text = (
        f"🗄️ *BIN MANAGEMENT*\n"
        f"{SEP}\n"
        f"Total Custom BINs: `{custom_bin_count}`\n\n"
        f"Use this panel to add custom BINs to the generator.\n"
        f"The bot auto-detects the card network from the BIN prefix."
    )
    buttons = [
        [InlineKeyboardButton("✏️ Add BIN Manually", callback_data="admin_bin_manual")],
        [InlineKeyboardButton("📁 Upload BIN .txt File", callback_data="admin_bin_upload")],
        [InlineKeyboardButton("📋 View Custom BINs", callback_data="admin_bin_view_0")],
        [InlineKeyboardButton("🗑️ Delete a BIN", callback_data="admin_bin_delete")],
        [InlineKeyboardButton("📤 Export All BINs", callback_data="admin_bin_export")],
        [InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")],
    ]
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── Callback Handler ────────────────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    # ── Main Menu ──
    if data == "main_menu":
        if authorized_check(user.id):
            expiry = db.get_subscription_expiry(user.id)
            remaining = expiry - datetime.utcnow() if expiry else timedelta(0)
            h, rem = divmod(int(max(remaining.total_seconds(), 0)), 3600)
            m = rem // 60
            exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC") if expiry else "N/A"
            text = (
                f"╔══════════════════════════╗\n"
                f"║   🃏 CC GENERATOR BOT   ║\n"
                f"╚══════════════════════════╝\n\n"
                f"Welcome back, *{user.first_name}*! ✨\n\n"
                f"✅ *Subscription Active*\n"
                f"⏳ Expires: `{exp_str}`\n"
                f"🕐 Remaining: `{h}h {m}m`\n\n"
                f"Choose an option below:"
            )
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                          reply_markup=main_menu_keyboard(user.id))
        else:
            await query.edit_message_text(
                "🔒 Subscription expired. Use `/redeem YOUR-KEY` to reactivate.",
                parse_mode=ParseMode.MARKDOWN)

    elif data == "profile":
        user_data = db.get_user(user.id)
        if not user_data:
            return
        expiry = db.get_subscription_expiry(user.id)
        status = "✅ Active" if authorized_check(user.id) else "❌ Inactive"
        exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC") if expiry else "None"
        join = (user_data.get("join_date") or "N/A")[:10]
        text = (
            f"👤 *USER PROFILE*\n{SEP}\n"
            f"🆔 *ID:* `{user.id}`\n"
            f"📛 *Name:* {user.first_name}\n"
            f"👤 *Username:* @{user.username or 'N/A'}\n"
            f"📅 *Joined:* `{join}`\n{SEP}\n"
            f"🔐 *Status:* {status}\n"
            f"⏳ *Expires:* `{exp_str}`\n{SEP}\n"
            f"💳 *Generations:* `{user_data.get('total_generations', 0)}`\n"
            f"🃏 *Total Cards:* `{user_data.get('total_cards_generated', 0)}`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=back_to_main_keyboard())

    elif data == "stats":
        stats = db.get_stats()
        active = db.get_active_users_count()
        text = (
            f"📊 *BOT STATISTICS*\n{SEP}\n"
            f"👥 Total Users: `{stats.get('total_users', 0)}`\n"
            f"✅ Active: `{active}`\n"
            f"🔑 Licences Issued: `{stats.get('total_licenses_generated', 0)}`\n"
            f"🎟 Licences Redeemed: `{stats.get('total_licenses_redeemed', 0)}`\n"
            f"💳 Cards Generated: `{stats.get('total_cc_generated', 0)}`\n"
            f"🗄️ Custom BINs: `{db.get_custom_bins_count()}`\n"
            f"⏱ Uptime: `{get_uptime()}`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=back_to_main_keyboard())

    elif data == "about":
        text = (
            f"ℹ️ *ABOUT THIS BOT*\n{SEP}\n"
            f"🃏 *CC Generator Bot* generates *test credit/debit card numbers* for payment gateway testing and development.\n\n"
            f"⚠️ *For developers only.* Do NOT use for illegal activities.\n\n"
            f"🌐 *Supported:*\n"
            f"• 60+ Countries • 200+ Banks\n"
            f"• 9 Card Networks • Custom BINs\n"
            f"• Up to 10,000 cards • .txt file output\n"
            f"{SEP}\nv2.0.0 — Built for Developers"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=back_to_main_keyboard())

    elif data == "help":
        text = (
            f"🆘 *HELP & COMMANDS*\n{SEP}\n"
            f"📌 *Commands:*\n"
            f"/start — Main menu\n"
            f"/redeem `[KEY]` — Redeem a licence\n"
            f"/admin — Admin panel\n\n"
            f"📌 *How to Generate:*\n"
            f"1. Tap 💳 Generate Test Cards\n"
            f"2. Pick countries (multiple OK)\n"
            f"3. Pick bank (optional)\n"
            f"4. Pick networks (Visa, MC...)\n"
            f"5. Pick card category\n"
            f"6. Debit / Credit / Both\n"
            f"7. Enter quantity (1–10,000)\n"
            f"8. Download .txt file 📄\n\n"
            f"📌 *Output Format:*\n"
            f"`CARD_NUMBER|MM|YY|CVV`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=back_to_main_keyboard())

    # ── Admin ──
    elif data == "admin_panel":
        if not is_admin(user.id):
            await query.answer("❌ Unauthorized", show_alert=True)
            return
        await show_admin_panel(update, context)

    elif data == "admin_stats":
        if not is_admin(user.id):
            return
        stats = db.get_stats()
        active = db.get_active_users_count()
        all_users = db.get_all_users()
        text = (
            f"📊 *FULL ADMIN STATISTICS*\n{SEP}\n"
            f"🤖 Uptime: `{get_uptime()}`\n"
            f"👥 Total Users: `{stats.get('total_users', 0)}`\n"
            f"✅ Active: `{active}`\n"
            f"❌ Inactive: `{len(all_users) - active}`\n"
            f"🔑 Licences Generated: `{stats.get('total_licenses_generated', 0)}`\n"
            f"🎟 Licences Redeemed: `{stats.get('total_licenses_redeemed', 0)}`\n"
            f"💳 Cards Generated: `{stats.get('total_cc_generated', 0)}`\n"
            f"🗄️ Custom BINs: `{db.get_custom_bins_count()}`\n"
            f"📅 Time: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
        )
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("admin_users_"):
        if not is_admin(user.id):
            return
        page = int(data.split("_")[-1])
        per_page = 8
        all_users = db.get_all_users()
        total = len(all_users)
        chunk = all_users[page * per_page: (page + 1) * per_page]
        lines = [f"👥 *USER LIST* (Page {page + 1})\n{SEP}"]
        for u in chunk:
            expiry = u.get("subscription_expiry")
            is_active = (datetime.utcnow() < datetime.fromisoformat(expiry)) if expiry else False
            status = "✅" if is_active else "❌"
            name = (u.get("first_name") or "Unknown")[:15]
            lines.append(f"{status} `{u['user_id']}` — {name} | 💳{u.get('total_cards_generated', 0)}")
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_users_{page - 1}"))
        if (page + 1) * per_page < total:
            nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_users_{page + 1}"))
        buttons = []
        if nav:
            buttons.append(nav)
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin_panel")])
        await query.edit_message_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_view_lic":
        if not is_admin(user.id):
            return
        lics = db.get_all_licenses(15)
        lines = [f"🔑 *RECENT LICENCES*\n{SEP}"]
        for lic in lics:
            used = "✅ Used" if lic["is_used"] else "🟢 Available"
            dur = f"{lic['duration_value']}{lic['duration_unit']}"
            lines.append(f"`{lic['key']}` | {dur} | {used}")
        if not lics:
            lines.append("No licences generated yet.")
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="admin_panel")]]
        await query.edit_message_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_gen_lic":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_lic_count"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "🔑 *Generate Licences*\n\nHow many licence keys to create?\n_Type a number (e.g. 5):_",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_revoke":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_revoke_id"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text("❌ *Revoke User Access*\n\nSend the User ID to revoke:",
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_broadcast":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_broadcast"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text("📣 *Broadcast Message*\n\nSend the message to broadcast:",
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("admin_dur_"):
        if not is_admin(user.id):
            return
        duration_str = data[len("admin_dur_"):]
        val = int(duration_str[:-1])
        unit = duration_str[-1].upper()
        count = context.user_data.get("lic_count", 1)
        keys = db.generate_license_keys(count, val, unit, user.id)
        unit_labels = {"M": "Minute(s)", "H": "Hour(s)", "D": "Day(s)"}
        label = unit_labels.get(unit, unit)
        text = f"✅ *{count} Licence(s) Generated!*\n⏱ Duration: `{val} {label}`\n\n🔑 *Keys:*\n"
        for k in keys:
            text += f"`{k}`\n"
        context.user_data["admin_state"] = None
        buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_custom_dur":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_custom_dur"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "⏱ *Custom Duration*\n\nEnter duration (e.g. `2H`, `30M`, `7D`):",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    # ── BIN Management ──
    elif data == "admin_bin_menu":
        if not is_admin(user.id):
            return
        await show_bin_menu(query, context)

    elif data == "admin_bin_manual":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "bin_wait_bin"
        context.user_data["pending_bin"] = {}
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_bin_menu")]]
        await query.edit_message_text(
            "✏️ *Add BIN Manually*\n\n"
            "Send the *6–8 digit BIN* to add:\n"
            "_Example: `411111`_\n\n"
            "The bot will auto-detect the card network.",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_bin_upload":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "bin_wait_file"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_bin_menu")]]
        await query.edit_message_text(
            "📁 *Upload BIN File*\n\n"
            "Send a `.txt` file with BINs.\n\n"
            "Supported formats:\n"
            "• One BIN per line: `411111`\n"
            "• CSV: `BIN,BANK,COUNTRY,TYPE`\n"
            "  _e.g. `411111,Chase,US,credit`_\n\n"
            "Lines starting with `#` are ignored.\n"
            "Country must be 2-letter code (US, GB, IN...)\n"
            "Type: `credit`, `debit`, or `both`",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("admin_bin_view_"):
        if not is_admin(user.id):
            return
        page = int(data.split("_")[-1])
        bins = db.get_custom_bins(500)
        total = len(bins)
        per_page = CUSTOM_BINS_PER_PAGE
        chunk = bins[page * per_page:(page + 1) * per_page]
        lines = [f"🗄️ *CUSTOM BINs* (Page {page + 1} / {max(1, (total + per_page - 1) // per_page)})\n"
                 f"Total: `{total}`\n{SEP}"]
        for b in chunk:
            lines.append(
                f"`{b['bin']}` | {b['network']} | {b['bank_name'][:15]} | "
                f"{b['country_code']} | {b['card_type']}"
            )
        if not chunk:
            lines.append("No custom BINs added yet.")
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"admin_bin_view_{page - 1}"))
        if (page + 1) * per_page < total:
            nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"admin_bin_view_{page + 1}"))
        buttons = []
        if nav:
            buttons.append(nav)
        buttons.append([InlineKeyboardButton("◀️ Back", callback_data="admin_bin_menu")])
        await query.edit_message_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_bin_delete":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "bin_wait_delete"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_bin_menu")]]
        await query.edit_message_text("🗑️ *Delete BIN*\n\nSend the BIN to delete:",
                                      parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "admin_bin_export":
        if not is_admin(user.id):
            return
        bins = db.get_all_custom_bins()
        if not bins:
            await query.answer("No custom BINs to export.", show_alert=True)
            return
        lines = ["# CC Generator Bot - Custom BINs Export",
                 f"# Exported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                 f"# Total: {len(bins)}",
                 "# Format: BIN,BANK_NAME,COUNTRY_CODE,CARD_TYPE,NETWORK",
                 ""]
        for b in bins:
            lines.append(f"{b['bin']},{b['bank_name']},{b['country_code']},{b['card_type']},{b['network']}")
        content = "\n".join(lines)
        file_obj = io.BytesIO(content.encode("utf-8"))
        file_obj.name = f"custom_bins_{datetime.utcnow().strftime('%Y%m%d')}.txt"
        await query.message.reply_document(
            document=file_obj,
            filename=file_obj.name,
            caption=f"📤 Custom BINs Export — `{len(bins)}` BINs",
            parse_mode=ParseMode.MARKDOWN)
        await query.answer("✅ Exported!")

    elif data.startswith("bin_confirm_type_"):
        if not is_admin(user.id):
            return
        card_type = data[len("bin_confirm_type_"):]
        pending = context.user_data.get("pending_bin", {})
        pending["card_type"] = card_type
        bin_code = pending["bin"]
        bank_name = pending["bank_name"]
        country_code = pending["country_code"]
        country_name = pending["country_name"]
        network = pending["network"]
        # Save
        added = db.add_custom_bin(bin_code, bank_name, country_code, country_name,
                                   network, card_type, user.id)
        context.user_data["admin_state"] = None
        context.user_data["pending_bin"] = {}
        if added:
            text = (
                f"✅ *BIN Added Successfully!*\n{SEP}\n"
                f"🔢 BIN: `{bin_code}`\n"
                f"💳 Network: `{network}`\n"
                f"🏦 Bank: `{bank_name}`\n"
                f"🌍 Country: `{country_code}` — {country_name}\n"
                f"💰 Type: `{card_type}`"
            )
        else:
            text = f"⚠️ BIN `{bin_code}` already exists in the database."
        buttons = [[InlineKeyboardButton("➕ Add Another", callback_data="admin_bin_manual")],
                   [InlineKeyboardButton("◀️ BIN Menu", callback_data="admin_bin_menu")]]
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                      reply_markup=InlineKeyboardMarkup(buttons))

    # ── CC Generation ──
    elif data == "gen_start":
        if not authorized_check(user.id):
            await query.edit_message_text(
                "🔒 Subscription expired. Use `/redeem YOUR-KEY` to reactivate.",
                parse_mode=ParseMode.MARKDOWN)
            return
        context.user_data.clear()
        context.user_data["selected_countries"] = []
        await show_country_page(query, context, 0)

    elif data.startswith("country_page_"):
        page = int(data.split("_")[-1])
        await show_country_page(query, context, page)

    elif data.startswith("toggle_country_"):
        code = data[len("toggle_country_"):]
        selected = context.user_data.get("selected_countries", [])
        if code in selected:
            selected.remove(code)
        else:
            selected.append(code)
        context.user_data["selected_countries"] = selected
        page = context.user_data.get("country_page", 0)
        await show_country_page(query, context, page)

    elif data == "confirm_countries":
        if not context.user_data.get("selected_countries"):
            await query.answer("⚠️ Select at least 1 country!", show_alert=True)
            return
        context.user_data["selected_banks"] = []
        await show_bank_selection(query, context, 0)

    elif data.startswith("bank_page_"):
        page = int(data.split("_")[-1])
        await show_bank_selection(query, context, page)

    elif data.startswith("toggle_bank_"):
        bank = data[len("toggle_bank_"):]
        selected = context.user_data.get("selected_banks", [])
        if bank in selected:
            selected.remove(bank)
        else:
            selected.append(bank)
        context.user_data["selected_banks"] = selected
        page = context.user_data.get("bank_page", 0)
        await show_bank_selection(query, context, page)

    elif data in ("skip_bank", "confirm_banks"):
        await show_network_selection(query, context)

    elif data.startswith("toggle_network_"):
        net = data[len("toggle_network_"):]
        selected = context.user_data.get("selected_networks", [])
        if net in selected:
            selected.remove(net)
        else:
            selected.append(net)
        context.user_data["selected_networks"] = selected
        await show_network_selection(query, context)

    elif data == "all_networks":
        context.user_data["selected_networks"] = list(cg.ALL_NETWORKS)
        await show_network_selection(query, context)

    elif data == "confirm_networks":
        if not context.user_data.get("selected_networks"):
            await query.answer("⚠️ Select at least 1 network!", show_alert=True)
            return
        await show_card_category_selection(query, context)

    elif data.startswith("toggle_category_"):
        cat = data[len("toggle_category_"):]
        selected = context.user_data.get("selected_categories", [])
        if cat in selected:
            selected.remove(cat)
        else:
            selected.append(cat)
        context.user_data["selected_categories"] = selected
        await show_card_category_selection(query, context)

    elif data == "all_categories":
        context.user_data["selected_categories"] = list(cg.CARD_CATEGORIES)
        await show_card_category_selection(query, context)

    elif data == "confirm_categories":
        if not context.user_data.get("selected_categories"):
            await query.answer("⚠️ Select at least 1 category!", show_alert=True)
            return
        await show_debit_credit_selection(query, context)

    elif data.startswith("select_dc_"):
        context.user_data["card_dc"] = data[len("select_dc_"):]
        await show_count_selection(query, context)

    elif data.startswith("set_count_"):
        context.user_data["card_count"] = int(data[len("set_count_"):])
        context.user_data["awaiting_custom_count"] = False
        await show_generation_confirm(query, context)

    elif data == "custom_count":
        context.user_data["awaiting_custom_count"] = True
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="gen_start")]]
        await query.edit_message_text(
            "✏️ *Enter Custom Count*\n\nType a number between 1 and 10,000:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif data == "confirm_generate":
        await do_generate(query, context, user)

    elif data == "gen_start_over":
        context.user_data.clear()
        context.user_data["selected_countries"] = []
        await show_country_page(query, context, 0)


# ─── Generation Flow Screens ─────────────────────────────────────────────────

async def show_country_page(query, context, page: int):
    context.user_data["country_page"] = page
    selected = context.user_data.get("selected_countries", [])
    countries = cg.get_countries_list()
    total = len(countries)
    per_page = COUNTRIES_PER_PAGE
    chunk = countries[page * per_page:(page + 1) * per_page]
    header = (
        f"🌍 *SELECT COUNTRIES*\n{SEP}\n"
        f"Select one or more countries.\n"
        f"Selected: {len(selected)} | Page {page + 1}/{(total + per_page - 1) // per_page}\n{SEP}"
    )
    buttons = []
    for code, name in chunk:
        tick = "✅ " if code in selected else ""
        buttons.append([InlineKeyboardButton(f"{tick}{name}", callback_data=f"toggle_country_{code}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"country_page_{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"country_page_{page + 1}"))
    if nav:
        buttons.append(nav)
    bottom = []
    if selected:
        bottom.append(InlineKeyboardButton(f"✅ Confirm ({len(selected)})", callback_data="confirm_countries"))
    bottom.append(InlineKeyboardButton("🏠 Cancel", callback_data="main_menu"))
    buttons.append(bottom)
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def show_bank_selection(query, context, page: int):
    context.user_data["bank_page"] = page
    selected_countries = context.user_data.get("selected_countries", [])
    selected_banks = context.user_data.get("selected_banks", [])
    banks = cg.get_banks_for_countries(selected_countries)
    total = len(banks)
    per_page = BANKS_PER_PAGE
    chunk = banks[page * per_page:(page + 1) * per_page]
    header = (
        f"🏦 *SELECT BANKS* (Optional)\n{SEP}\n"
        f"Pick specific banks or skip for all.\n"
        f"Selected: {len(selected_banks)} | Page {page + 1}/{max(1, (total + per_page - 1) // per_page)}\n{SEP}"
    )
    buttons = []
    for bank in chunk:
        tick = "✅ " if bank in selected_banks else ""
        buttons.append([InlineKeyboardButton(f"{tick}{bank}", callback_data=f"toggle_bank_{bank}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ Prev", callback_data=f"bank_page_{page - 1}"))
    if (page + 1) * per_page < total:
        nav.append(InlineKeyboardButton("Next ▶️", callback_data=f"bank_page_{page + 1}"))
    if nav:
        buttons.append(nav)
    row = [InlineKeyboardButton("⏭️ Skip (All Banks)", callback_data="skip_bank")]
    if selected_banks:
        row.append(InlineKeyboardButton(f"✅ Confirm ({len(selected_banks)})", callback_data="confirm_banks"))
    buttons.append(row)
    buttons.append([InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")])
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def show_network_selection(query, context):
    selected = context.user_data.get("selected_networks", [])
    header = (
        f"💳 *SELECT CARD NETWORKS*\n{SEP}\n"
        f"Choose which networks to include.\n"
        f"Selected: {len(selected)}\n{SEP}"
    )
    buttons = []
    row = []
    for i, net in enumerate(cg.ALL_NETWORKS):
        tick = "✅ " if net in selected else ""
        row.append(InlineKeyboardButton(f"{tick}{net}", callback_data=f"toggle_network_{net}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    action_row = [InlineKeyboardButton("🔘 Select All", callback_data="all_networks")]
    if selected:
        action_row.append(InlineKeyboardButton(f"✅ Confirm ({len(selected)})", callback_data="confirm_networks"))
    buttons.append(action_row)
    buttons.append([InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")])
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def show_card_category_selection(query, context):
    selected = context.user_data.get("selected_categories", [])
    header = (
        f"🏷️ *SELECT CARD CATEGORIES*\n{SEP}\n"
        f"Choose card tier/category.\n"
        f"Selected: {len(selected)}\n{SEP}"
    )
    buttons = []
    row = []
    for cat in cg.CARD_CATEGORIES:
        tick = "✅ " if cat in selected else ""
        row.append(InlineKeyboardButton(f"{tick}{cat}", callback_data=f"toggle_category_{cat}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    action_row = [InlineKeyboardButton("🔘 Select All", callback_data="all_categories")]
    if selected:
        action_row.append(InlineKeyboardButton(f"✅ Confirm ({len(selected)})", callback_data="confirm_categories"))
    buttons.append(action_row)
    buttons.append([InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")])
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


async def show_debit_credit_selection(query, context):
    buttons = [
        [InlineKeyboardButton("💳 Credit", callback_data="select_dc_credit"),
         InlineKeyboardButton("🏧 Debit", callback_data="select_dc_debit")],
        [InlineKeyboardButton("💳+🏧 Both", callback_data="select_dc_both")],
        [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        f"💰 *SELECT CARD TYPE*\n{SEP}\nChoose Credit, Debit, or Both.\n{SEP}",
        parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_count_selection(query, context):
    presets = [10, 25, 50, 100, 250, 500, 1000, 5000, 10000]
    buttons = []
    row = []
    for p in presets:
        row.append(InlineKeyboardButton(str(p), callback_data=f"set_count_{p}"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("✏️ Custom Number", callback_data="custom_count")])
    buttons.append([InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")])
    await query.edit_message_text(
        f"🔢 *HOW MANY CARDS?*\n{SEP}\nSelect a preset or enter custom.\nMax: 10,000\n{SEP}",
        parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_generation_confirm(query, context):
    countries = context.user_data.get("selected_countries", [])
    banks = context.user_data.get("selected_banks", [])
    networks = context.user_data.get("selected_networks", [])
    categories = context.user_data.get("selected_categories", [])
    dc = context.user_data.get("card_dc", "credit")
    count = context.user_data.get("card_count", 10)
    country_names = [name for code, name in cg.get_countries_list() if code in countries]
    banks_str = ", ".join(banks) if banks else "All Banks"
    nets_str = ", ".join(networks) if networks else "All Networks"
    cats_str = ", ".join(categories) if categories else "All"
    text = (
        f"✅ *GENERATION SUMMARY*\n{SEP}\n"
        f"🌍 Countries: {', '.join(country_names)}\n"
        f"🏦 Banks: {banks_str}\n"
        f"💳 Networks: {nets_str}\n"
        f"🏷️ Categories: {cats_str}\n"
        f"💰 Type: {dc.capitalize()}\n"
        f"🔢 Count: `{count:,}` cards\n"
        f"📄 Output: `.txt` file download\n{SEP}\n"
        f"Ready to generate?"
    )
    buttons = [
        [InlineKeyboardButton("🚀 Generate!", callback_data="confirm_generate")],
        [InlineKeyboardButton("🔄 Start Over", callback_data="gen_start_over")],
        [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN,
                                  reply_markup=InlineKeyboardMarkup(buttons))


# ─── Card Generation & File Output ───────────────────────────────────────────

async def do_generate(query, context, user):
    countries = context.user_data.get("selected_countries", [])
    banks = context.user_data.get("selected_banks", []) or None
    networks = context.user_data.get("selected_networks", []) or None
    total_count = context.user_data.get("card_count", 10)
    dc = context.user_data.get("card_dc", "credit")

    types_to_gen = ["credit", "debit"] if dc == "both" else [dc]
    count_per_type = max(1, total_count // len(types_to_gen))

    await query.edit_message_text(
        f"⚙️ *Generating {total_count:,} cards...*\n\n"
        f"{progress_bar(0, total_count)}\n\nPlease wait...",
        parse_mode=ParseMode.MARKDOWN)

    # Load custom BINs once
    custom_bins_list = db.get_all_custom_bins()

    all_cards = []
    generated = 0
    chunk_size = max(50, total_count // 10)

    for card_type in types_to_gen:
        remaining = count_per_type
        while remaining > 0:
            batch = min(chunk_size, remaining)
            cards = cg.generate_cards_with_custom(
                countries, banks, networks, card_type, batch, custom_bins_list)
            all_cards.extend(cards)
            generated += len(cards)
            remaining -= batch
            try:
                await query.edit_message_text(
                    f"⚙️ *Generating {total_count:,} cards...*\n\n"
                    f"{progress_bar(generated, total_count)}\n\n"
                    f"Generated: `{generated:,}` / `{total_count:,}`",
                    parse_mode=ParseMode.MARKDOWN)
            except Exception:
                pass
            await asyncio.sleep(0.2)

    db.update_user_stats(user.id, len(all_cards))

    # Build .txt file
    country_names = [name for code, name in cg.get_countries_list() if code in countries]
    nets_str = ", ".join(networks) if networks else "All Networks"
    banks_str = ", ".join(banks) if banks else "All Banks"

    header_lines = [
        "╔══════════════════════════════════════════╗",
        "║         CC GENERATOR BOT — RESULTS       ║",
        "╚══════════════════════════════════════════╝",
        f"Generated : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Countries : {', '.join(country_names)}",
        f"Networks  : {nets_str}",
        f"Banks     : {banks_str}",
        f"Type      : {dc.capitalize()}",
        f"Total     : {len(all_cards):,} cards",
        f"Format    : CARD_NUMBER|MONTH|YEAR|CVV",
        "=" * 44,
        "",
    ]

    card_lines = [cg.format_card(c) for c in all_cards]
    file_content = "\n".join(header_lines + card_lines)

    file_obj = io.BytesIO(file_content.encode("utf-8"))
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"cards_{len(all_cards)}_{timestamp}.txt"
    file_obj.name = filename

    # Update progress to done
    await query.edit_message_text(
        f"✅ *Generation Complete!*\n\n"
        f"{progress_bar(total_count, total_count)}\n\n"
        f"💳 `{len(all_cards):,}` cards ready — sending file...",
        parse_mode=ParseMode.MARKDOWN)

    # Preview: first 5 cards inline
    preview_lines = [f"`{cg.format_card(c)}`" for c in all_cards[:5]]
    preview_text = "\n".join(preview_lines)
    if len(all_cards) > 5:
        preview_text += f"\n_...and {len(all_cards) - 5:,} more in the file_"

    buttons = [
        [InlineKeyboardButton("🔄 Generate More", callback_data="gen_start_over")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]

    # Send file
    await query.message.reply_document(
        document=file_obj,
        filename=filename,
        caption=(
            f"✅ *{len(all_cards):,} cards generated*\n\n"
            f"📄 Format: `CARD_NUMBER|MM|YY|CVV`\n\n"
            f"*Preview (first 5):*\n{preview_text}"
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


# ─── Message Handler ─────────────────────────────────────────────────────────

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (update.message.text or "").strip()
    admin_state = context.user_data.get("admin_state")
    awaiting_custom_count = context.user_data.get("awaiting_custom_count", False)

    # Custom card count input
    if awaiting_custom_count:
        try:
            count = int(text)
            if count < 1 or count > 10000:
                await update.message.reply_text("❌ Enter a number between 1 and 10,000.")
                return
            context.user_data["card_count"] = count
            context.user_data["awaiting_custom_count"] = False
            countries = context.user_data.get("selected_countries", [])
            banks = context.user_data.get("selected_banks", [])
            networks = context.user_data.get("selected_networks", [])
            categories = context.user_data.get("selected_categories", [])
            dc = context.user_data.get("card_dc", "credit")
            country_names = [name for code, name in cg.get_countries_list() if code in countries]
            summary = (
                f"✅ *GENERATION SUMMARY*\n{SEP}\n"
                f"🌍 Countries: {', '.join(country_names)}\n"
                f"🏦 Banks: {', '.join(banks) if banks else 'All Banks'}\n"
                f"💳 Networks: {', '.join(networks) if networks else 'All Networks'}\n"
                f"🏷️ Categories: {', '.join(categories) if categories else 'All'}\n"
                f"💰 Type: {dc.capitalize()}\n"
                f"🔢 Count: `{count:,}` cards\n"
                f"📄 Output: `.txt` file download\n{SEP}\nReady to generate?"
            )
            buttons = [
                [InlineKeyboardButton("🚀 Generate!", callback_data="confirm_generate")],
                [InlineKeyboardButton("🔄 Start Over", callback_data="gen_start_over")],
                [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
            ]
            await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup(buttons))
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please enter a valid integer.")
        return

    # Admin state machine
    if admin_state and is_admin(user.id):
        await handle_admin_state(update, context, admin_state, text)
        return

    # Unauthorized / unrecognized
    if not authorized_check(user.id):
        await update.message.reply_text(
            "🔒 Not authorised. Use `/redeem YOUR-KEY` to activate.",
            parse_mode=ParseMode.MARKDOWN)
        return

    await update.message.reply_text("Use the menu below to navigate.",
                                    reply_markup=main_menu_keyboard(user.id))


async def handle_admin_state(update: Update, context: ContextTypes.DEFAULT_TYPE,
                              state: str, text: str):
    user = update.effective_user

    # ── Licence generation ──
    if state == "waiting_lic_count":
        try:
            count = int(text)
            if count < 1 or count > 1000:
                await update.message.reply_text("❌ Enter a number between 1 and 1000.")
                return
            context.user_data["lic_count"] = count
            context.user_data["admin_state"] = "waiting_lic_duration"
            presets = [("1H", "1 Hour"), ("6H", "6 Hours"), ("12H", "12 Hours"),
                       ("1D", "1 Day"), ("3D", "3 Days"), ("7D", "7 Days"),
                       ("30D", "30 Days"), ("1M", "1 Minute"), ("5M", "5 Minutes")]
            buttons = []
            row = []
            for code, label in presets:
                row.append(InlineKeyboardButton(label, callback_data=f"admin_dur_{code}"))
                if len(row) == 3:
                    buttons.append(row)
                    row = []
            if row:
                buttons.append(row)
            buttons.append([InlineKeyboardButton("✏️ Custom Duration", callback_data="admin_custom_dur")])
            buttons.append([InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")])
            await update.message.reply_text(
                f"🔑 Generating *{count}* licence(s).\n\nChoose duration:",
                parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number.")

    elif state == "waiting_custom_dur":
        text_upper = text.upper().strip()
        try:
            unit = text_upper[-1]
            val = int(text_upper[:-1])
            if unit not in ("M", "H", "D") or val < 1:
                raise ValueError
            count = context.user_data.get("lic_count", 1)
            keys = db.generate_license_keys(count, val, unit, user.id)
            unit_labels = {"M": "Minute(s)", "H": "Hour(s)", "D": "Day(s)"}
            result_text = (f"✅ *{count} Licence(s) Generated!*\n"
                           f"⏱ Duration: `{val} {unit_labels.get(unit, unit)}`\n\n🔑 *Keys:*\n")
            for k in keys:
                result_text += f"`{k}`\n"
            context.user_data["admin_state"] = None
            buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
            await update.message.reply_text(result_text, parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup(buttons))
        except (ValueError, IndexError):
            await update.message.reply_text("❌ Invalid format. Use like: `2H`, `30M`, `7D`",
                                            parse_mode=ParseMode.MARKDOWN)

    elif state == "waiting_revoke_id":
        try:
            target_id = int(text.strip())
            db.revoke_user(target_id)
            context.user_data["admin_state"] = None
            buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
            await update.message.reply_text(f"✅ Access revoked for user `{target_id}`.",
                                            parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup(buttons))
        except ValueError:
            await update.message.reply_text("❌ Invalid User ID.")

    elif state == "waiting_broadcast":
        all_users = db.get_all_users()
        sent = failed = 0
        for u in all_users:
            try:
                await context.bot.send_message(
                    chat_id=u["user_id"],
                    text=f"📣 *ANNOUNCEMENT*\n\n{text}",
                    parse_mode=ParseMode.MARKDOWN)
                sent += 1
            except Exception:
                failed += 1
            await asyncio.sleep(0.05)
        context.user_data["admin_state"] = None
        buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
        await update.message.reply_text(
            f"📣 Broadcast complete!\n✅ Sent: {sent} | ❌ Failed: {failed}",
            reply_markup=InlineKeyboardMarkup(buttons))

    # ── BIN management ──
    elif state == "bin_wait_bin":
        bin_code = text.strip().replace(" ", "").replace("-", "")
        if not bin_code.isdigit() or not (6 <= len(bin_code) <= 8):
            await update.message.reply_text("❌ BIN must be 6–8 digits. Try again:")
            return
        # Auto-detect network
        network = bd.detect_network(bin_code)
        # Check duplicate
        if db.bin_exists(bin_code):
            buttons = [[InlineKeyboardButton("◀️ BIN Menu", callback_data="admin_bin_menu")]]
            await update.message.reply_text(
                f"⚠️ BIN `{bin_code}` already exists in the database.",
                parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))
            return
        context.user_data["pending_bin"]["bin"] = bin_code
        context.user_data["pending_bin"]["network"] = network
        context.user_data["admin_state"] = "bin_wait_bank"
        await update.message.reply_text(
            f"✅ BIN: `{bin_code}`\n"
            f"💳 Auto-detected Network: *{network}*\n\n"
            f"Now enter the *bank name* for this BIN:\n_e.g. Chase, HDFC Bank, Barclays_",
            parse_mode=ParseMode.MARKDOWN)

    elif state == "bin_wait_bank":
        bank_name = text.strip()
        if len(bank_name) < 2:
            await update.message.reply_text("❌ Bank name too short. Try again:")
            return
        context.user_data["pending_bin"]["bank_name"] = bank_name
        context.user_data["admin_state"] = "bin_wait_country"
        await update.message.reply_text(
            f"🏦 Bank: *{bank_name}*\n\n"
            f"Now enter the *country code* (2 letters):\n"
            f"_e.g. US, GB, IN, DE, JP, AU, SG_",
            parse_mode=ParseMode.MARKDOWN)

    elif state == "bin_wait_country":
        country_code = text.strip().upper()
        if len(country_code) != 2 or not country_code.isalpha():
            await update.message.reply_text("❌ Enter a valid 2-letter country code (e.g. US, GB, IN):")
            return
        country_name = bd.get_country_name(country_code)
        context.user_data["pending_bin"]["country_code"] = country_code
        context.user_data["pending_bin"]["country_name"] = country_name
        context.user_data["admin_state"] = "bin_wait_type"
        pending = context.user_data["pending_bin"]
        buttons = [
            [InlineKeyboardButton("💳 Credit", callback_data="bin_confirm_type_credit"),
             InlineKeyboardButton("🏧 Debit", callback_data="bin_confirm_type_debit")],
            [InlineKeyboardButton("💳+🏧 Both", callback_data="bin_confirm_type_both")],
            [InlineKeyboardButton("◀️ Cancel", callback_data="admin_bin_menu")],
        ]
        await update.message.reply_text(
            f"🌍 Country: *{country_code}* — {country_name}\n\n"
            f"📋 *Summary so far:*\n"
            f"BIN: `{pending['bin']}`\n"
            f"Network: `{pending['network']}`\n"
            f"Bank: `{pending['bank_name']}`\n"
            f"Country: `{country_code}`\n\n"
            f"Last step — choose card type:",
            parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif state == "bin_wait_delete":
        bin_code = text.strip().replace(" ", "")
        deleted = db.delete_custom_bin(bin_code)
        context.user_data["admin_state"] = None
        buttons = [[InlineKeyboardButton("◀️ BIN Menu", callback_data="admin_bin_menu")]]
        if deleted:
            await update.message.reply_text(f"✅ BIN `{bin_code}` deleted.",
                                            parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await update.message.reply_text(f"❌ BIN `{bin_code}` not found.",
                                            parse_mode=ParseMode.MARKDOWN,
                                            reply_markup=InlineKeyboardMarkup(buttons))


# ─── Document Handler (BIN File Upload) ──────────────────────────────────────

async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        return
    if context.user_data.get("admin_state") != "bin_wait_file":
        return

    doc = update.message.document
    if not doc:
        return

    filename = doc.file_name or ""
    if not filename.lower().endswith(".txt"):
        await update.message.reply_text("❌ Please send a `.txt` file.",
                                        parse_mode=ParseMode.MARKDOWN)
        return

    # Download file
    file = await context.bot.get_file(doc.file_id)
    file_bytes = await file.download_as_bytearray()
    content = file_bytes.decode("utf-8", errors="ignore")

    # Parse BINs
    parsed = bd.parse_bin_file(content)
    if not parsed:
        await update.message.reply_text(
            "❌ No valid BINs found in file.\n\n"
            "Format: `BIN,BANK_NAME,COUNTRY_CODE,CARD_TYPE`\n"
            "Or one BIN per line.", parse_mode=ParseMode.MARKDOWN)
        return

    # Process each BIN
    added = []
    skipped_dup = []
    skipped_invalid = []

    for entry in parsed:
        bin_code = entry["bin"]
        bank_name = entry.get("bank_name", "Custom Bank")
        country_code = entry.get("country_code", "US")
        card_type = entry.get("card_type", "credit")

        if db.bin_exists(bin_code):
            skipped_dup.append(bin_code)
            continue

        network = bd.detect_network(bin_code)
        if network == "Unknown":
            skipped_invalid.append(bin_code)
            continue

        country_name = bd.get_country_name(country_code)
        success = db.add_custom_bin(
            bin_code, bank_name, country_code, country_name,
            network, card_type, user.id)
        if success:
            added.append(bin_code)
        else:
            skipped_dup.append(bin_code)

    context.user_data["admin_state"] = None

    text = (
        f"📁 *BIN File Processed!*\n{SEP}\n"
        f"📄 File: `{filename}`\n"
        f"📊 Total in file: `{len(parsed)}`\n\n"
        f"✅ *Added:* `{len(added)}`\n"
        f"⚠️ *Skipped (duplicate):* `{len(skipped_dup)}`\n"
        f"❌ *Skipped (invalid BIN):* `{len(skipped_invalid)}`\n"
    )
    if added:
        preview = added[:10]
        text += f"\n*Added BINs preview:*\n" + " | ".join(f"`{b}`" for b in preview)
        if len(added) > 10:
            text += f"\n_...and {len(added) - 10} more_"

    buttons = [[InlineKeyboardButton("◀️ BIN Menu", callback_data="admin_bin_menu")]]
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=InlineKeyboardMarkup(buttons))


# ─── Background Jobs ──────────────────────────────────────────────────────────

async def check_expired_subscriptions(context: ContextTypes.DEFAULT_TYPE):
    pass


async def post_init(application):
    await application.bot.set_my_commands([
        BotCommand("start", "Open the main menu"),
        BotCommand("redeem", "Redeem a licence key"),
        BotCommand("admin", "Admin panel"),
    ])


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    db.init_db()
    start_health_server()

    token = config.BOT_TOKEN
    if not token:
        logger.error("BOT_TOKEN not set!")
        return

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("redeem", cmd_redeem))
    app.add_handler(CommandHandler("admin", cmd_admin))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_expired_subscriptions, interval=60, first=60)

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

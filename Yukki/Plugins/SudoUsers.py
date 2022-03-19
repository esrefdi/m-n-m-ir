import asyncio
import os
import shutil
import subprocess
from sys import version as pyver

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import LOG_SESSION, OWNER_ID
from Yukki import BOT_ID, BOT_USERNAME, MUSIC_BOT_NAME, OWNER_ID, SUDOERS, app
from Yukki.Database import (add_gban_user, add_off, add_on, add_sudo,
                            get_active_chats, get_served_chats, get_sudoers,
                            is_gbanned_user, remove_active_chat,
                            remove_gban_user, remove_served_chat, remove_sudo,
                            set_video_limit)

__MODULE__ = "Sudoİstifadəçilər"
__HELP__ = """


/sudolist 
    Botun sudo istifadəçi siyahısını yoxlayın.


 **Qeyd:**
 Yalnız Sudo İstifadəçiləri üçün. 


/addsudo [İstifadəçi adı və ya istifadəçiyə cavab]
 - Botun Sudo İstifadəçilərinə İstifadəçi əlavə etmək üçün.

 /delsudo [İstifadəçi adı və ya istifadəçiyə cavab]
 - İstifadəçini Botun Sudo İstifadəçilərindən Silmək üçün.

/maintenance [enable / disable]
- Aktivləşdirildikdə, Bot texniki xidmət rejiminə keçir.  İndi heç kim Musiqi oynaya bilməz!

/logger [enable / disable]
- Aktivləşdirildikdə, Bot axtarış edilən sorğuları qeyd edən qrupda qeyd edir.

/clean
- Temp faylları və qeydləri təmizləyin.
"""
# Add Sudo Users!


@app.on_message(filters.command("addsudo") & filters.user(OWNER_ID))
async def useradd(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "İstifadəçinin mesajına cavab verin və ya istifadəçi adı/user_id verin."
             )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id in SUDOERS:
            return await message.reply_text(
                f"{user.mention} artıq sudo istifadəçisidir."
             )
        added = await add_sudo(user.id)
        if added:
            await message.reply_text(
                f"Sudo İstifadəçilərinə **{user.mention}** əlavə edildi."
            )
            os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        else:
            await message.reply_text("Failed")
        return
    if message.reply_to_message.from_user.id in SUDOERS:
        return await message.reply_text(
            f"{message.reply_to_message.from_user.mention} artıq sudo istifadəçisidir."
         )
    added = await add_sudo(message.reply_to_message.from_user.id)
    if added:
        await message.reply_text(
            f"Sudo İstifadəçilərinə **{message.reply_to_message.from_user.mention}** əlavə edildi"
        )
        os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    else:
        await message.reply_text("Failed")
    return


@app.on_message(filters.command("delsudo") & filters.user(OWNER_ID))
async def userdel(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "İstifadəçinin mesajına cavab verin və ya istifadəçi adı/user_id verin."
             )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id not in SUDOERS:
            return await message.reply_text(f"Bot Sudo-nun bir hissəsi deyil.")
        removed = await remove_sudo(user.id)
        if removed:
            await message.reply_text(
                f"**{user.mention}** {MUSIC_BOT_NAME}-nin Sudo-dan silindi."
            )
            return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
        await message.reply_text(f"Bir şey səhv oldu.")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    if user_id not in SUDOERS:
        return await message.reply_text(
            f"Not a part of {MUSIC_BOT_NAME}'s Sudo."
        )
    removed = await remove_sudo(user_id)
    if removed:
        await message.reply_text(
            f"**{mention}** {MUSIC_BOT_NAME}-nin Sudo-dan silindi."
        )
        return os.system(f"kill -9 {os.getpid()} && python3 -m Yukki")
    await message.reply_text(f"Bir şey səhv oldu.")


@app.on_message(filters.command("sudolist"))
async def sudoers_list(_, message: Message):
    sudoers = await get_sudoers()
    text = "⭐️<u> **Sahiblər:**</u>\n"
    sex = 0
    for x in OWNER_ID:
        try:
            user = await app.get_users(x)
            user = user.first_name if not user.mention else user.mention
            sex += 1
        except Exception:
            continue
        text += f"{sex}➤ {user}\n"
    smex = 0
    for count, user_id in enumerate(sudoers, 1):
        if user_id not in OWNER_ID:
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += "\n⭐️<u> **Sudo İstifadəçiləri:**</u>\n"
                sex += 1
                text += f"{sex}➤ {user}\n"
            except Exception:
                continue
    if not text:
        await message.reply_text("Sudo İstifadəçiləri Yoxdur")
    else:
        await message.reply_text(text)


### Video Limit


@app.on_message(
    filters.command(["set_video_limit", f"set_video_limit@{BOT_USERNAME}"])
    & filters.user(SUDOERS)
)
async def set_video_limit_kid(_, message: Message):
    if len(message.command) != 2:
        usage = "**İstifadə:**\n/set_video_limit [İcazə verilən söhbətlərin sayı]"
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    try:
        limit = int(state)
    except:
        return await message.reply_text(
             "Lütfü təyin etmək üçün rəqəmsal nömrələrdən istifadə edin."
         )
    await set_video_limit(141414, limit)
    await message.reply_text(
        f"Video Zənglərin Maksimum Limiti Söhbətlərə {limit} Təyin edilib."
    )


## Maintenance Yukki


@app.on_message(filters.command("maintenance") & filters.user(SUDOERS))
async def maintenance(_, message):
    usage = "**İstifadə:**\n/maintenance [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 1
        await add_on(user_id)
        await message.reply_text("Enabled for Maintenance")
    elif state == "disable":
        user_id = 1
        await add_off(user_id)
        await message.reply_text("Maintenance Mode Disabled")
    else:
        await message.reply_text(usage)


## Logger


@app.on_message(filters.command("logger") & filters.user(SUDOERS))
async def logger(_, message):
    if LOG_SESSION == "None":
        return await message.reply_text(
            "Heç bir Qeydiyyatçı Hesabı Müəyyən edilməmişdir.\n\nLütfən, <code>LOG_SESSION</code> parametrini təyin edin və sonra daxil olmağa cəhd edin."
        )
    usage = "**İstifadə:**\n/logger [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    chat_id = message.chat.id
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        user_id = 5
        await add_on(user_id)
        await message.reply_text("Enabled Logging")
    elif state == "disable":
        user_id = 5
        await add_off(user_id)
        await message.reply_text("Logging Disabled")
    else:
        await message.reply_text(usage)


## Gban Module


@app.on_message(filters.command("gban") & filters.user(SUDOERS))
async def ban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) < 2:
            await message.reply_text("**İstifadə:**\n/gban [USERNAME | USER_ID]")
            return
        user = message.text.split(None, 2)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        if user.id == from_user.id:
            return await message.reply_text(
                "Sən özünü gban etmək istəyirsən? Necə də axmaq!"
             )
        elif user.id == BOT_ID:
            await message.reply_text("Özümü bloklamalıyam? Lom Gedə Lom!")
        elif user.id in SUDOERS:
            await message.reply_text("Sudo istifadəçisini bloklamaq istəyirsiniz? Mal")
        else:
            await add_gban_user(user.id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**{user.mention} üçün Qlobal Qadağanın başlanğıcı qoyulur**\n\nGözlənilən vaxt: {len(served_chats)}"
            )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user.id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**{MUSIC_BOT_NAME} üçün yeni qlobal qadağa**__

 **Mənşə:**{message.chat.title} [`{message.chat.id}`]
**Sudo İstifadəçisi:** {from_user.mention}
 **Qadağan edilmiş İstifadəçi:** {user.mention}
 **Qadağan edilmiş İstifadəçi ID-si:** `{user.id}`
 **Söhbətlər:** {number_of_chats}"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
        return
    from_user_id = message.from_user.id
    from_user_mention = message.from_user.mention
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text("Özünüzü bloklamaq istəyirsiniz? Necə də axmaq!")
    elif user_id == BOT_ID:
        await message.reply_text("Özümü bloklamalıyam? Lmao Ded!")
    elif user_id in sudoers:
        await message.reply_text("Sudo istifadəçisini bloklamaq istəyirsiniz? KIDXZ")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if is_gbanned:
            await message.reply_text("Artıq banlanıb.")
        else:
            await add_gban_user(user_id)
            served_chats = []
            chats = await get_served_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
            m = await message.reply_text(
                f"**Qlobal Qadağanın {mention}** üzrə Başlanılması Gözlənilən Vaxtda : {len(served_chats)}" )
            number_of_chats = 0
            for sex in served_chats:
                try:
                    await app.ban_chat_member(sex, user_id)
                    number_of_chats += 1
                    await asyncio.sleep(1)
                except FloodWait as e:
                    await asyncio.sleep(int(e.x))
                except Exception:
                    pass
            ban_text = f"""
__**{MUSIC_BOT_NAME} üçün yeni qlobal qadağa**__

 **Mənşə:** {message.chat.title} [`{message.chat.id}`]
 **Sudo İstifadəçisi:** {from_user_mention}
 **Qadağan edilmiş İstifadəçi:** {qeyd}
 **Qadağan edilmiş İstifadəçi ID-si:** `{user_id}`
 **Söhbətlər:** {söhbətlərin_sayı}"""
            try:
                await m.delete()
            except Exception:
                pass
            await message.reply_text(
                f"{ban_text}",
                disable_web_page_preview=True,
            )
            return


@app.on_message(filters.command("ungban") & filters.user(SUDOERS))
async def unban_globally(_, message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "**İstifadə:**\n/ungban [USERNAME | USER_ID]"
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        from_user = message.from_user
        sudoers = await get_sudoers()
        if user.id == from_user.id:
            await message.reply_text("Özünüzü blokdan çıxarmaq istəyirsiniz?")
        elif user.id == BOT_ID:
            await message.reply_text("Özümü blokdan çıxarmalıyam?")
        elif user.id in sudoers:
            await message.reply_text("Sudo istifadəçiləri bloklana blokdan çıxarıla bilməz.")
        else:
            is_gbanned = await is_gbanned_user(user.id)
            if not is_gbanned:
                await message.reply_text("O, artıq azaddır, niyə onu təhqir edirsiniz?")
            else:
                await remove_gban_user(user.id)
                await message.reply_text(f"Ungbanned!")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    mention = message.reply_to_message.from_user.mention
    sudoers = await get_sudoers()
    if user_id == from_user_id:
        await message.reply_text("Özünüzü blokdan çıxarmaq istəyirsiniz?")
    elif user_id == BOT_ID:
        await message.reply_text(
            "Özümü blokdan çıxarmalıyam? Amma bloklanmamışam."
         )
    elif user_id in sudoers:
        await message.reply_text("Sudo istifadəçiləri bloklana blokdan çıxarıla bilməz.")
    else:
        is_gbanned = await is_gbanned_user(user_id)
        if not is_gbanned:
            await message.reply_text("He's already free, why bully him?")
        else:
            await remove_gban_user(user_id)
            await message.reply_text(f"Ungbanned!")


# Broadcast Message


@app.on_message(filters.command("broadcast_pin") & filters.user(SUDOERS))
async def broadcast_message_pin_silent(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=True)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**Yayımlanan Mesaj {sent} Çatlarda {pin} Pin ilə.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**İstifadə**:\n/broadcast [MESSAGE] və ya [Mesajı Cavab]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=True)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(
        f"**Broadcasted Message In {sent} Chats and {pin} Pins.**"
    )


@app.on_message(filters.command("broadcast_pin_loud") & filters.user(SUDOERS))
async def broadcast_message_pin_loud(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                try:
                    await m.pin(disable_notification=False)
                    pin += 1
                except Exception:
                    pass
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(
            f"**Broadcasted Message In {sent}  Chats with {pin} Pins.**"
        )
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    pin = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            try:
                await m.pin(disable_notification=False)
                pin += 1
            except Exception:
                pass
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(
        f"**Broadcasted Message In {sent} Chats and {pin} Pins.**"
    )


@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast(_, message):
    if not message.reply_to_message:
        pass
    else:
        x = message.reply_to_message.message_id
        y = message.chat.id
        sent = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await app.forward_messages(i, y, x)
                await asyncio.sleep(0.3)
                sent += 1
            except Exception:
                pass
        await message.reply_text(f"**Broadcasted Message In {sent} Chats.**")
        return
    if len(message.command) < 2:
        await message.reply_text(
            "**Usage**:\n/broadcast [MESSAGE] or [Reply to a Message]"
        )
        return
    text = message.text.split(None, 1)[1]
    sent = 0
    chats = []
    schats = await get_served_chats()
    for chat in schats:
        chats.append(int(chat["chat_id"]))
    for i in chats:
        try:
            m = await app.send_message(i, text=text)
            await asyncio.sleep(0.3)
            sent += 1
        except Exception:
            pass
    await message.reply_text(f"**Broadcasted Message In {sent} Chats.**")


# Clean


@app.on_message(filters.command("clean") & filters.user(SUDOERS))
async def clean(_, message):
    dir = "downloads"
    dir1 = "cache"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await message.reply_text("Successfully cleaned all **temp** dir(s)!")

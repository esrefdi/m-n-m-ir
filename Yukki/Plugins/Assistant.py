import random

from pyrogram import filters
from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQueryResultArticle,
                            InlineQueryResultPhoto, InputTextMessageContent,
                            Message)

from Yukki import ASSISTANT_PREFIX, SUDOERS, app, random_assistant
from Yukki.Database import get_assistant, save_assistant
from Yukki.Utilities.assistant import get_assistant_details

__MODULE__ = "Assistant"
__HELP__ = f"""


/checkassistant
- Söhbətinizin ayrılmış Assistant ı yoxlayın


**Qeyd:**
 - Yalnız Sudo İstifadəçiləri üçün

{ASSISTANT_PREFIX[0]}blok [İstifadəçi Mesajına Cavab Verin]
 - İstifadəçini köməkçi hesabından bloklayır.

{ASSISTANT_PREFIX[0]}blokdan çıxarın [İstifadəçi Mesajına Cavab Verin]
 - İstifadəçini Assistent Hesabından blokdan çıxarır.

{ASSISTANT_PREFIX[0]}təsdiq edin [ İstifadəçi Mesajına Cavab Verin]
 - İstifadəçini DM üçün təsdiqləyir.

{ASSISTANT_PREFIX[0]}təsdiq et [ İstifadəçi Mesajına Cavab Verin]
 - İstifadəçini DM üçün təsdiq etmir.

{ASSISTANT_PREFIX[0]}pfp [Fotoya cavab verin]
 - Assistant hesab PFP-ni dəyişir.

 {ASSISTANT_PREFIX[0]}bio [Bio mətn]
 - Assistant Hesabının Tərkibi dəyişdirilir.

/changeassistant [ASS NÖMRƏSİ]
 - Əvvəlki Assistant ı yenisi ilə dəyişdirin.

/setassistant [ASS NÖMRƏSİ və ya Təsadüfi]
 - Söhbət üçün Assistant hesabı təyin edin.
 """


ass_num_list = ["1", "2", "3", "4", "5"]


@app.on_message(filters.command("changeassistant") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**İstifadə:**\n/changeassistant Assistant  [ASS_NO]\n\nBunlardan Birini seçin\n{' | '.join(ass_num_list)}"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    num = message.text.split(None, 1)[1].strip()
    if num not in ass_num_list:
        return await message.reply_text(usage)
    ass_num = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Qabaqcadan saxlanmış köməkçi tapılmadı./setassistant vasitəsilə Assistent təyin edə bilərsiniz"
        )
    else:
        ass = _assistant["saveassistant"]
    assis = {
        "saveassistant": ass_num,
    }
    await save_assistant(message.chat.id, "assistant", assis)
    await message.reply_text(
        f"**Dəyişən Assistent**\n\nAssistent Hesabı **{ass}**-dan **{ass_num}**-a dəyişdirildi"
    )


ass_num_list2 = ["1", "2", "3", "4", "5", "Random"]


@app.on_message(filters.command("setassistant") & filters.user(SUDOERS))
async def assis_change(_, message: Message):
    usage = f"**İstifadə:**\n/setassistant [ASS_NO və ya Random]\n\nOnlardan seçin\n{' | '.join(ass_num_list2)}\n\nTəsadüfi Assistent qurmaq üçün 'Təsadüfi' istifadə edin"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    query = message.text.split(None, 1)[1].strip()
    if query not in ass_num_list2:
        return await message.reply_text(usage)
    if str(query) == "Random":
        ran_ass = random.choice(random_assistant)
    else:
        ran_ass = int(message.text.strip().split()[1])
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        await message.reply_text(
            f"**__Yukki Musiqi Bot Köməkçisi Ayrıldı__**\n\nAssistent No. **{ran_ass}**"
        )
        assis = {
            "saveassistant": ran_ass,
        }
        await save_assistant(message.chat.id, "assistant", assis)
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Qabaqcadan Yadda Saxlanmış Assistent Nömrəsi {ass}.\n\nSiz /changeassistant Vasitəsilə dəyişə bilərsiniz"
        )


@app.on_message(filters.command("checkassistant") & filters.group)
async def check_ass(_, message: Message):
    _assistant = await get_assistant(message.chat.id, "assistant")
    if not _assistant:
        return await message.reply_text(
            "Əvvəlcədən Saxlanmış Assistent Tapılmadı.\in\Siz Assistenti /play vasitəsilə quraşdıra bilərsiniz"
        )
    else:
        ass = _assistant["saveassistant"]
        return await message.reply_text(
            f"Qabaqcadan Saxlanmış Assistent Tapıldı\n\nKöməkçi Nömrəsi {ass} "
        )

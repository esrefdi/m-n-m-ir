import asyncio
import math
import os
import dotenv
import random
import shutil
from datetime import datetime
from time import strftime, time

import heroku3
import requests
import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import Client, filters
from pyrogram.types import Message

from config import (HEROKU_API_KEY, HEROKU_APP_NAME, UPSTREAM_BRANCH,
                    UPSTREAM_REPO)
from Yukki import LOG_GROUP_ID, MUSIC_BOT_NAME, SUDOERS, app
from Yukki.Database import get_active_chats, remove_active_chat, remove_active_video_chat
from Yukki.Utilities.heroku import is_heroku, user_input
from Yukki.Utilities.paste import isPreviewUp, paste_queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


__MODULE__ = "Server"
__HELP__ = f"""

**Qeyd:**
 **Yalnız Sudo İstifadəçiləri üçün**

/get_log
- Heroku-dan son 100 sətir qeydini alın.

 /get_var
 - Heroku və ya .env-dən konfiqurasiya var əldə edin.

 /del_var
 - Heroku və ya .env-də hər hansı bir var silin.

 /set_var [Var Adı] [Dəyər]
 - Heroku və ya .env-də Var təyin edin və ya Var-ı yeniləyin.  Var və onun dəyərini boşluqla ayırın.

/usage
 - Dyno İstifadəsini əldə edin.

 /update
 - Botunuzu yeniləyin.

 /restart
 - Botu yenidən başladın [Bütün yükləmələr, keş, xam fayllar da silinəcək].
"""


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(HEROKU_API_KEY),
    "https",
    str(HEROKU_APP_NAME),
    "HEAD",
    "main",
]


@app.on_message(filters.command("get_log") & filters.user(SUDOERS))
async def log_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
    else:
        return await message.reply_text("Yalnız Heroku Proqramları üçün")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        happ = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            "Lütfən, Heroku API Açarınızın, Proqramınızın adının heroku-da düzgün konfiqurasiya edildiyinə əmin olun"
        )
    data = happ.get_log()
    if len(data) > 1024:
        link = await paste_queue(data)
        url = link + "/index.txt"
        return await message.reply_text(
            f"Budur Tətbiqinizin Qeydiyyatı[{HEROKU_APP_NAME}]\n\n[Logları yoxlamaq üçün buraya klikləyin]({url})"
        )
    else:
        return await message.reply_text(data)


@app.on_message(filters.command("get_var") & filters.user(SUDOERS))
async def varget_(client, message):
    usage = "**Usage:**\n/get_var [Var Name]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
            )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfən, Heroku API Açarınızın, Proqramınızın adının heroku-da düzgün konfiqurasiya edildiyinə əmin olun"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            return await message.reply_text(
                f"**Heroku Konfiqurasiyası:**\n\n**{check_var}:** `{heroku_config[check_var]}`"
            )
        else:
            return await message.reply_text("No such Var")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env not found.")
        output = dotenv.get_key(path, check_var)
        if not output:
            return await message.reply_text("No such Var")
        else:
            return await message.reply_text(f".env:\n\n**{check_var}:** `{str(output)}`")


@app.on_message(filters.command("del_var") & filters.user(SUDOERS))
async def vardel_(client, message):
    usage = "**Usage:**\n/del_var [Var Name]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    check_var = message.text.split(None, 2)[1]
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
             )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfən, Heroku API Açarınızın, Proqramınızın adının heroku-da düzgün konfiqurasiya edildiyinə əmin olun"
            )
        heroku_config = happ.config()
        if check_var in heroku_config:
            await message.reply_text(
                f"**Heroku Var Silinməsi:**\n\n`{check_var}` uğurla silindi."
            )
            del heroku_config[check_var]
        else:
            return await message.reply_text(f"No such Var")
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env not found.")
        output = dotenv.unset_key(path, check_var)
        if not output[0]:
            return await message.reply_text("No such Var")
        else:
            return await message.reply_text(f".env Var Silinməsi:\n\n`{check_var}` uğurla silindi. Botu yenidən başlatmaq üçün /restart əmrini icra edin.")

@app.on_message(filters.command("set_var") & filters.user(SUDOERS))
async def set_var(client, message):
    usage = "**Usage:**\n/set_var [Var Name] [Var Value]"
    if len(message.command) < 3:
        return await message.reply_text(usage)
    to_set = message.text.split(None, 2)[1].strip()
    value = message.text.split(None, 2)[2].strip()
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
             )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
        try:
            Heroku = heroku3.from_key(HEROKU_API_KEY)
            happ = Heroku.app(HEROKU_APP_NAME)
        except BaseException:
            return await message.reply_text(
                "Lütfən, Heroku API Açarınızın, Proqramınızın adının heroku-da düzgün konfiqurasiya edildiyinə əmin olun"
            )
        heroku_config = happ.config()
        if to_set in heroku_config:
            await message.reply_text(
                f"**Heroku Var Yeniləmə:**\n\n`{to_set}` uğurla yeniləndi. Bot İndi Yenidən Başlayacaq."
            )
        else:
            await message.reply_text(
                f"`{to_set}` adlı Yeni Var əlavə edildi. Bot İndi Yenidən Başlayacaq."
             )
        heroku_config[to_set] = value
    else:
        path = dotenv.find_dotenv()
        if not path:
            return await message.reply_text(".env not found.")
        output = dotenv.set_key(path, to_set, value)
        if dotenv.get_key(path, to_set):
            return await message.reply_text(f"**.env Var Yeniləmə:**\n\n`{to_set}` uğurla yeniləndi. Botu yenidən başlatmaq üçün /restart əmrini icra edin.")
        else:
            return await message.reply_text(f"**. env dəyişəninin əlavəsi:** \n\n`{to_set}` uğurla əlavə edildi. Botu yenidən başlatmaq üçün /restart əmrini icra edin.")


@app.on_message(filters.command("usage") & filters.user(SUDOERS))
async def usage_dynos(client, message):
    ### Credits CatUserbot
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
             )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
    else:
        return await message.reply_text("Only for Heroku Apps")
    try:
        Heroku = heroku3.from_key(HEROKU_API_KEY)
        happ = Heroku.app(HEROKU_APP_NAME)
    except BaseException:
        return await message.reply_text(
            "Lütfən, Heroku API Açarınızın, Proqramınızın adının heroku-da düzgün konfiqurasiya edildiyinə əmin olun"
        )
    dyno = await message.reply_text("Heroku istifadəsinin yoxlanılması.  Zəhmət olmasa, gözləyin")
    account_id = Heroku.account().id
    useragent = (
        "Mozilla/5.0 (Linux; Android 10; SM-G975F) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/80.0.3987.149 Mobile Safari/537.36"
    )
    headers = {
        "İstifadəçi-Agent": useragent,
        "İcazə": f"Daşıyıcı {HEROKU_API_KEY}",
         "Qəbul edirəm": "application/vnd.heroku+json; version=3.account-quotas",
    }
    path = "/accounts/" + account_id + "/actions/get-quota"
    r = requests.get("https://api.heroku.com" + path, headers=headers)
    if r.status_code != 200:
        return await dyno.edit("Unable to fetch.")
    result = r.json()
    quota = result["account_quota"]
    quota_used = result["quota_used"]
    remaining_quota = quota - quota_used
    percentage = math.floor(remaining_quota / quota * 100)
    minutes_remaining = remaining_quota / 60
    hours = math.floor(minutes_remaining / 60)
    minutes = math.floor(minutes_remaining % 60)
    App = result["apps"]
    try:
        App[0]["quota_used"]
    except IndexError:
        AppQuotaUsed = 0
        AppPercentage = 0
    else:
        AppQuotaUsed = App[0]["quota_used"] / 60
        AppPercentage = math.floor(App[0]["quota_used"] * 100 / quota)
    AppHours = math.floor(AppQuotaUsed / 60)
    AppMinutes = math.floor(AppQuotaUsed % 60)
    await asyncio.sleep(1.5)
    text = f"""
**DYNO İSTİFADƏ**

<u>Usage:</u>
Ümumi istifadə: `{AppHours}`**h**  `{AppMinutes}`**m**  [`{AppPercentage}`**%**]

<u>Qalan Kvota:</u>
Ümumi Sol: `{hours}`**h**  `{minutes}`**m**  [`{percentage}`**%**]"""
    return await dyno.edit(text)


@app.on_message(filters.command("update") & filters.user(SUDOERS))
async def update_(client, message):
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yeniləmək üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
             )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yeniləyin!</b>"
             )
    response = await message.reply_text("Checking for available updates...")
    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("Git Command Error")
    except InvalidGitRepositoryError:
        return await response.edit("Invalid Git Repsitory")
    to_exc = f"git fetch origin {UPSTREAM_BRANCH} &> /dev/null"
    os.system(to_exc)
    await asyncio.sleep(7)
    verification = ""
    REPO_ = repo.remotes.origin.url.split(".git")[0]  # main git repository
    for checks in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        verification = str(checks.count())
    if verification == "":
        return await response.edit("Bot is up-to-date!")
    updates = ""
    ordinal = lambda format: "%d%s" % (
        format,
        "tsnrhtdd"[
            (format // 10 % 10 != 1) * (format % 10 < 4) * format % 10 :: 4
        ],
    )
    for info in repo.iter_commits(f"HEAD..origin/{UPSTREAM_BRANCH}"):
        updates += f"<b>➣ #{info.count()}: [{info.summary}]({REPO_}/commit/{info}) by -> {info.author}</b>\n\t\t\t\t<b>➥ Commited on:</b> {ordinal(int(datetime.fromtimestamp(info.committed_date).strftime('%d')))} {datetime.fromtimestamp(info.committed_date).strftime('%b')}, {datetime.fromtimestamp(info.committed_date).strftime('%Y')}\n\n"
    _update_response_ = "<b>Bot üçün yeni güncəlləmə əlçatandır!</b>\n\n➣ İndi Yeniləmələr Təklif olunur</code>\n\n**<u>Yeniləmələr:</u>**\n\n  "
    _final_updates_ = _update_response_ + updates
    if len(_final_updates_) > 4096:
        link = await paste_queue(updates)
        url = link + "/index.txt"
        nrs = await response.edit(
            f"<b>Bot üçün yeni güncəlləmə əlçatandır!</b>\n\n➣ Yeniləmələri İndi İtmək</code>\n\n**<u>Yeniləmələr:</u>**\n\  n[Yeniləmələri yoxlamaq üçün buraya klikləyin]({url})"
        )
    else:
        nrs = await response.edit(
            _final_updates_, disable_web_page_preview=True
        )
    os.system("git stash &> /dev/null && git pull")
    if await is_heroku():
        try:
            await response.edit(
                f"{nrs.text}\n\nBot Heroku-da uğurla yeniləndi!  İndi, bot yenidən başlayana qədər 2-3 dəqiqə gözləyin!"
            )
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
            return
        except Exception as err:
            await response.edit(
                f"{nrs.text}\n\nYenidən yükləməyə başlayarkən xəta baş verdi!  Lütfən, daha sonra yenidən cəhd edin və ya əlavə məlumat üçün qeydləri yoxlayın."
            )
            return await app.send_message(
                LOG_GROUP_ID,
                f"AN EXCEPTION OCCURRED AT #UPDATER DUE TO: <code>{err}</code>",
            )
    else:
        await response.edit(
            f"{nrs.text}\n\nBot uğurla yeniləndi!  İndi, bot yenidən işə düşənə qədər 1-2 dəqiqə gözləyin!"
        )
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()
    return


@app.on_message(filters.command("restart") & filters.user(SUDOERS))
async def restart_(_, message):
    response = await message.reply_text("Restarting....")
    if await is_heroku():
        if HEROKU_API_KEY == "" and HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ ALINDI!</b>\n\nTətbiqinizi yenidən başlatmaq üçün müvafiq olaraq `HEROKU_API_KEY` və `HEROKU_APP_NAME` variantlarını quraşdırmalısınız!"
             )
        elif HEROKU_API_KEY == "" or HEROKU_APP_NAME == "":
            return await message.reply_text(
                "<b>HEROKU TƏTBİQİ AŞPAQLANIB!</b>\n\n<b>Hər ikisini</b> `HEROKU_API_KEY` **və** `HEROKU_APP_NAME` <b>varları düzgün əlavə etdiyinizə əmin olun.  uzaqdan yenidən başladın!</b>"
             )
        try:
            served_chats = []
            try:
                chats = await get_active_chats()
                for chat in chats:
                    served_chats.append(int(chat["chat_id"]))
            except Exception as e:
                pass
            for x in served_chats:
                try:
                    await app.send_message(
                        x,
                        f"{MUSIC_BOT_NAME} indicə özünü yenidən başladıb. Problemlərə görə üzr istəyirik.\n\n10-15 saniyədən sonra oynamağa başlayın again.",
                    )
                    await remove_active_chat(x)
                    await remove_active_video_chat(x)
                except Exception:
                    pass
            heroku3.from_key(HEROKU_API_KEY).apps()[HEROKU_APP_NAME].restart()
            await response.edit(
                "**Heroku Restart**\n\nYenidən yükləmə uğurla başladıldı! Bot yenidən işə salınana qədər 1-2 dəqiqə gözləyin."
            )
            return
        except Exception as err:
            await response.edit(
                "Yenidən yükləməyə başlayarkən xəta baş verdi! Lütfən, sonra yenidən cəhd edin və ya əlavə məlumat üçün qeydləri yoxlayın."
             )
            return
    else:
        served_chats = []
        try:
            chats = await get_active_chats()
            for chat in chats:
                served_chats.append(int(chat["chat_id"]))
        except Exception as e:
            pass
        for x in served_chats:
            try:
                await app.send_message(
                    x,
                    f"{MUSIC_BOT_NAME} indicə özünü yenidən işə saldı. Problemlərə görə üzr istəyirik.\n\n10-15 saniyədən sonra yenidən oynamağa başlayın.",
                 )
                await remove_active_chat(x)
                await remove_active_video_chat(x)
            except Exception:
                pass
        A = "downloads"
        B = "raw_files"
        C = "cache"
        D = "search"
        try:
            shutil.rmtree(A)
            shutil.rmtree(B)
            shutil.rmtree(C)
            shutil.rmtree(D)
        except:
            pass
        await asyncio.sleep(2)
        try:
            os.mkdir(A)
        except:
            pass
        try:
            os.mkdir(B)
        except:
            pass
        try:
            os.mkdir(C)
        except:
            pass
        try:
            os.mkdir(D)
        except:
            pass
        await response.edit(
            "Yenidən yükləmə uğurla başladıldı! Bot yenidən başlayana qədər 1-2 dəqiqə gözləyin."
        )
        os.system(f"kill -9 {os.getpid()} && Mən İşləyirəm hohohoyy")

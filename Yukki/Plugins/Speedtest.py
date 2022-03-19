import os

import speedtest
import wget
from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import BOT_ID, SUDOERS, app
from Yukki.Utilities.formatters import bytes

__MODULE__ = "Speedtest"
__HELP__ = """

/speedtest 
- Server gecikmə və sürətini yoxlayın.

 """


@app.on_message(filters.command("speedtest") & ~filters.edited)
async def statsguwid(_, message):
    m = await message.reply_text("Qaçış sürəti testi")
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = await m.edit("Endirmə SpeedTest-in icrası")
        test.download()
        m = await m.edit("Yükləmə Sürət Testi işləyir")
        test.upload()
        test.results.share()
        result = test.results.dict()
    except Exception as e:
        return await m.edit(e)
    m = await m.edit("SpeedTest Nəticələrinin Paylaşılması")
    path = wget.download(result["share"])

    output = f"""**Sürət Test Nəticələri**
    
<u>**Müştəri:**</u>
 **__ISP:__** {result['client']['isp']}
**__Country:__** {result['client']['country']}
  
<u>**Server:**</u>
 **__Ad:__** {result['server']['name']}
**__Ölkə:__** {result['server']['country']}, {result['server']['cc']}
**__Sponsor:__** {result['server']['sponsor']}
**__Gecikmə:__** {result['server']['latency']}  
**__Ping:__** {result['ping']}"""
    msg = await app.send_photo(
        chat_id=message.chat.id, photo=path, caption=output
    )
    os.remove(path)
    await m.delete()

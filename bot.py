import os
import time
import asyncio
import logging
import pyromod.listen
from datetime import datetime, timedelta
from pytz import timezone
from pyrogram import Client, idle, __version__
from pyrogram.raw.all import layer
from pyrogram.errors import FloodWait, RPCError
from config import Config
from aiohttp import web
from route import web_server
import pyrogram.utils
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --
pyrogram.utils.MIN_CHANNEL_ID = -1002964099736
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --
PORT = Config.PORT
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --
class Bot(Client):
    def __init__(self):
        super().__init__(
            name="rexbots",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.start_time = time.time()
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.uptime = Config.BOT_UPTIME
        print(f"{me.first_name} Is Started.....✨️")
        uptime_seconds = int(time.time() - self.start_time)
        uptime_string = str(timedelta(seconds=uptime_seconds))
        for chat_id in [Config.LOG_CHANNEL, Config.SUPPORT_CHAT]:
            if not chat_id:
                continue
            try:
                curr = datetime.now(timezone("Asia/Kolkata"))
                date = curr.strftime('%d %B, %Y')
                time_str = curr.strftime('%I:%M:%S %p')
                await self.send_photo(
                    chat_id=chat_id,
                    photo=Config.START_PIC,
                    caption=(
                        "**I ʀᴇsᴛᴀʀᴛᴇᴅ ᴀɢᴀɪɴ !**\n\n"
                        f"ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​: `{uptime_string}`"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/EternalsHelplineBot")]]
                    )
                )
            except Exception as e:
                print(
                    f"Failed to send message in chat {chat_id}: {e}\n"
                    f"  -> If this says CHANNEL_INVALID/PEER_ID_INVALID: make sure "
                    f"this bot account is a member (ideally admin) of chat {chat_id}, "
                    f"and that the ID is current (LOG_CHANNEL/SUPPORT_CHAT env vars)."
                )
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --
async def _run_health_server():
    """Bind the health-check HTTP port immediately, independent of Telegram/
    Mongo. Koyeb (and Render/Railway) poll this port to decide whether the
    instance is healthy. If it never opens (e.g. because Pyrogram crashed
    during plugin loading before reaching this point), the platform
    restart-loops the container, and every restart re-attempts Telegram bot
    auth -- which is exactly what causes FloodWait bans. Starting this first,
    before touching Telegram at all, decouples that failure mode.

    Always binds on $PORT regardless of WEBHOOK so the service stays
    deployable on platforms that require an open HTTP port."""
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    await web.TCPSite(app_runner, "0.0.0.0", PORT).start()
    logging.info(f"Health-check web server listening on 0.0.0.0:{PORT}")
    return app_runner


async def _run_bot_with_backoff():
    """Start the Pyrogram client, with bounded backoff on FloodWait/RPC auth
    errors so a persistently bad credential can't spiral into an ever-worse
    FloodWait ban via rapid crash/restart cycles. Non-auth runtime errors are
    left to propagate normally (Koyeb's own restart policy handles those)."""
    max_attempts = 3
    attempt = 0
    bot = Bot()
    while True:
        attempt += 1
        try:
            await bot.start()
            await idle()
            await bot.stop()
            return
        except FloodWait as e:
            wait_for = int(e.value) + 5
            logging.error(
                f"Telegram FloodWait hit during startup: must wait {e.value}s. "
                f"This almost always means the container crash-looped and "
                f"retried bot auth too many times in a row (bad DB_URL, bad "
                f"API_ID/API_HASH, etc. causing repeated restarts). "
                f"Sleeping {wait_for}s before giving up this attempt "
                f"({attempt}/{max_attempts}) instead of exiting immediately "
                f"and letting Koyeb hammer Telegram again right away."
            )
            if attempt >= max_attempts:
                logging.error(
                    "Giving up after repeated FloodWait errors. Fix the "
                    "underlying config issue (see earlier logs) and wait out "
                    "the flood-wait window before redeploying."
                )
                raise
            await asyncio.sleep(wait_for)
        except RPCError as e:
            logging.error(
                f"Telegram rejected bot startup: {e}. This is almost always "
                f"a bad API_ID/API_HASH/BOT_TOKEN combination -- check them "
                f"in your Koyeb environment variables. Not retrying "
                f"immediately to avoid another FloodWait."
            )
            raise


def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Health server first, unconditionally, before anything Telegram-related.
    loop.run_until_complete(_run_health_server())
    try:
        loop.run_until_complete(_run_bot_with_backoff())
    except (FloodWait, RPCError):
        # Keep the process (and the already-bound health server) alive for a
        # short grace period instead of exiting instantly, so Koyeb doesn't
        # immediately spin up a fresh restart on top of a FloodWait we're
        # already inside.
        logging.error("Bot failed to start. Staying up briefly before exiting so Koyeb's restart isn't instantaneous.")
        loop.run_until_complete(asyncio.sleep(30))
        raise
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# --

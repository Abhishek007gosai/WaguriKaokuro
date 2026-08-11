import asyncio
import logging
import time
from datetime import datetime, timedelta

import pyromod.listen  # noqa: F401  — patches pyrogram for client.listen()
from aiohttp import web
from pyrogram import Client, idle
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone

from config import Config
from route import web_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

PORT = Config.PORT


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="rexbots",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=50,
            plugins={"root": "plugins"},
            sleep_threshold=15,
        )
        self.start_time = time.time()

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.mention = me.mention
        self.username = me.username
        self.uptime = Config.BOT_UPTIME
        print(f"{me.first_name} Is Started.....✨️")

        if Config.LOG_CHANNEL:
            try:
                uptime_seconds = int(time.time() - self.start_time)
                uptime_string = str(timedelta(seconds=uptime_seconds))
                curr = datetime.now(timezone("Asia/Kolkata"))
                await self.send_photo(
                    chat_id=Config.LOG_CHANNEL,
                    photo=Config.START_PIC,
                    caption=(
                        "**I ʀᴇsᴛᴀʀᴛᴇᴅ ᴀɢᴀɪɴ !**\n\n"
                        f"ɪ ᴅɪᴅɴ'ᴛ sʟᴇᴘᴛ sɪɴᴄᴇ​: `{uptime_string}`"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("ᴜᴘᴅᴀᴛᴇs", url="https://t.me/")]]
                    ),
                )
            except Exception as e:
                logging.warning(
                    "Could not send startup message to LOG_CHANNEL (%s): %s. "
                    "Unset LOG_CHANNEL or add the bot as admin there.",
                    Config.LOG_CHANNEL,
                    e,
                )


async def _run_health_server():
    """HTTP health endpoint for Koyeb/Render. Must bind before Telegram auth
    fails so the platform does not restart-loop the container."""
    app_runner = web.AppRunner(await web_server())
    await app_runner.setup()
    await web.TCPSite(app_runner, "0.0.0.0", PORT).start()
    logging.info("Health-check web server listening on 0.0.0.0:%s", PORT)
    return app_runner


def _rebind_motor():
    """Recreate the Motor client on the *current* running event loop.

    Import-time AsyncIOMotorClient binds to whatever loop existed then (often
    a default loop created by pyromod/pyrogram imports). That causes:
      RuntimeError: Future attached to a different loop
    on every DB call and, via cascading errors, on every /start reply.
    """
    try:
        from helper import database as dbmod

        dbmod.rexbots = dbmod.Seishiro(Config.DB_URL, Config.DB_NAME)
        logging.info("Motor client rebound to the running event loop")
    except Exception as e:
        logging.error("Failed to rebind Motor client: %s", e)


async def _run_bot():
    _rebind_motor()
    bot = Bot()
    max_attempts = 3
    attempt = 0
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
                "FloodWait during startup (%ss). Attempt %s/%s. Sleeping %ss.",
                e.value,
                attempt,
                max_attempts,
                wait_for,
            )
            if attempt >= max_attempts:
                raise
            await asyncio.sleep(wait_for)
        except RPCError as e:
            logging.error(
                "Telegram rejected bot startup: %s. Check API_ID/API_HASH/BOT_TOKEN.",
                e,
            )
            raise


async def _async_main():
    await _run_health_server()
    try:
        await _run_bot()
    except (FloodWait, RPCError):
        logging.error(
            "Bot failed to start. Staying up 30s so Koyeb does not restart instantly."
        )
        await asyncio.sleep(30)
        raise


def main():
    """
    Use one explicit event loop for aiohttp + pyrogram + motor.

    asyncio.run() is avoided on purpose: imports (pyromod, etc.) can create a
    default loop first; asyncio.run() then creates a *second* loop, and Motor /
    Pyrogram end up with futures on different loops.
    """
    try:
        old = asyncio.get_event_loop_policy().get_event_loop()
        if old is not None and not old.is_running():
            old.close()
    except Exception:
        pass

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(_async_main())
    except KeyboardInterrupt:
        pass
    finally:
        try:
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            if pending:
                loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
            loop.run_until_complete(loop.shutdown_asyncgens())
        except Exception:
            pass
        loop.close()


if __name__ == "__main__":
    main()

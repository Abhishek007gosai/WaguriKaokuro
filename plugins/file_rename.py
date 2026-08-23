# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
import os
import re
import json
import time
import shutil
import asyncio
import logging
import uuid
import pytz
from datetime import datetime
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor  # Added missing import
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import rexbots
from plugins.start import (
    handle_verification_callback,
    send_verification_message,
    is_user_verified,
)
from config import Config
from functools import wraps
from os import makedirs
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
# Must NOT create asyncio.Semaphore at import time (binds to wrong loop).
_semaphore = None

def _get_semaphore():
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(3)
    return _semaphore
chat_data_cache = {}
FSUB_PIC = Config.FSUB_PIC
BOT_USERNAME = Config.BOT_USERNAME
OWNER_ID = Config.OWNER_ID
FSUB_LINK_EXPIRY = 10
thread_pool = ThreadPoolExecutor(max_workers=4)
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
# ========== Decorators ==========

def check_ban(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        user = await rexbots.col.find_one({"_id": user_id})
        if user and user.get("ban_status", {}).get("is_banned", False):
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cᴏɴᴛᴀᴄᴛ ʜᴇʀᴇ...!!", url="https://t.me/")]]
            )
            return await message.reply_text(
                "Wᴛғ ʏᴏᴜ ᴀʀᴇ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜsɪɴɢ ᴍᴇ ʙʏ ᴏᴜʀ ᴀᴅᴍɪɴ/ᴏᴡɴᴇʀ . Iғ ʏᴏᴜ ᴛʜɪɴᴋs ɪᴛ's ᴍɪsᴛᴀᴋᴇ ᴄʟɪᴄᴋ ᴏɴ ᴄᴏɴᴛᴀᴄᴛ ʜᴇʀᴇ...!!",
                reply_markup=keyboard
            )
        return await func(client, message, *args, **kwargs)
    return wrapper

# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
async def check_user_premium(user_id):
    """Check if user has premium access - handles missing method gracefully"""
    try:
        # First check if the method exists
        if hasattr(rexbots, 'has_premium_access'):
            return await rexbots.has_premium_access(user_id)
        else:
            # Fallback: Check database directly
            user_data = await rexbots.col.find_one({"_id": user_id})
            if not user_data:
                return False
            
            # Check for premium in user data
            premium_data = user_data.get("premium", {})
            
            # Check if premium is active and not expired
            is_premium = premium_data.get("is_premium", False)
            expiry_date = premium_data.get("expiry_date")
            
            if is_premium and expiry_date:
                if isinstance(expiry_date, datetime):
                    return expiry_date > datetime.utcnow()
                else:
                    return True
            
            return is_premium
    except Exception as e:
        logger.error(f"Error checking premium status: {e}")
        return False
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
def check_verification(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        logger.debug(f"check_verification decorator called for user {user_id}")
        
        try:
            text = message.text or message.caption
            if text and len(text) > 7:
                try:
                    param = text.split(" ", 1)[1]
                    if param.startswith("verify_"):
                        token = param[7:]
                        await handle_verification_callback(client, message, token)
                        return
                        
                except Exception as e:
                    logger.error(f"Error processing start parameter: {e}")
                    await message.reply_text(f"Error: {e}")
    
            # Step 1: Check if user has premium access - premium users bypass verification
            try:
                if await check_user_premium(user_id):
                    logger.debug(f"User {user_id} has premium, bypassing verification")
                    return await func(client, message, *args, **kwargs)
            except Exception as e:
                logger.error(f"Error checking premium status in decorator: {e}")
                # Continue with verification check even if premium check fails
            
            # Step 2: Get verification settings to check if verification is enabled
            settings = await rexbots.get_verification_settings()
            verify_status_1 = settings.get("verify_status_1", False)
            verify_status_2 = settings.get("verify_status_2", False)
            
            # If both verification systems are disabled, allow access
            if not verify_status_1 and not verify_status_2:
                logger.debug(f"Verification disabled, allowing user {user_id}")
                return await func(client, message, *args, **kwargs)
            
            # Step 3: Check if user is already verified (EXACTLY like /verify command)
            try:
                if await is_user_verified(user_id):
                    try:
                        user_data = await rexbots.col.find_one({"_id": user_id}) or {}
                        verification_data = user_data.get("verification", {})
                        
                        verified_time_1 = verification_data.get("verified_time_1")
                        verified_time_2 = verification_data.get("verified_time_2")
                        
                        current_time = datetime.utcnow()
                        
                        # Check if fully verified (shortener 1 within 24 hours)
                        if verified_time_1:
                            try:
                                if isinstance(verified_time_1, datetime) and current_time < verified_time_1 + timedelta(hours=24):
                                    time_left = timedelta(hours=24) - (current_time - verified_time_1)
                                    hours_left = time_left.seconds // 3600
                                    minutes_left = (time_left.seconds % 3600) // 60
                                    return await func(client, message, *args, **kwargs)
                            except Exception as e:
                                logger.error(f"Error checking verified_time_1: {e}")

                        # Check if fully verified (shortener 2 within 24 hours)
                        if verified_time_2:
                            try:
                                if isinstance(verified_time_2, datetime) and current_time < verified_time_2 + timedelta(hours=24):
                                    time_left = timedelta(hours=24) - (current_time - verified_time_2)
                                    hours_left = time_left.seconds // 3600
                                    minutes_left = (time_left.seconds % 3600) // 60
                                    return await func(client, message, *args, **kwargs)
                            except Exception as e:
                                logger.error(f"Error checking verified_time_2: {e}")
                                
                    except Exception as e:
                        logger.error(f"Error checking verification status: {e}")
            except Exception as e:
                logger.error(f"Error in is_user_verified check: {e}")

            
            # Step 4: User is NOT verified - send verification message
            logger.debug(f"User {user_id} is not verified, sending verification prompt")

            try:
                await send_verification_message(client, message)
            except Exception as e:
                logger.error(f"Error sending verification message in decorator: {e}")
                await message.reply_text(
                    f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @EternalsHelplineBot</i></b>\n"
                    f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {str(e)}</blockquote>"
                )
            return
            
        except Exception as e:
            logger.error(f"FATAL ERROR in check_verification decorator: {e}")
            await message.reply_text(
                f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @EternalsHelplineBot</i></b>\n"
                f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {str(e)}</blockquote>"
            )
            return
    
    return wrapper
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
def check_fsub(func):
    @wraps(func)
    async def wrapper(client, message, *args, **kwargs):
        user_id = message.from_user.id
        print(f"DEBUG: check_fsub decorator called for user {user_id}")

        async def is_sub(client, user_id, channel_id):
            try:
                member = await client.get_chat_member(channel_id, user_id)
                status = member.status
                return status in {
                    ChatMemberStatus.OWNER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.MEMBER
                }
            except UserNotParticipant:
                mode = await rexbots.get_channel_mode(channel_id)
                if mode == "on":
                    exists = await rexbots.req_user_exist(channel_id, user_id)
                    return exists
                return False
            except Exception as e:
                print(f"[!] Error in is_sub(): {e}")
                return False

        async def is_subscribed(client, user_id):
            channel_ids = await rexbots.show_channels()
            if not channel_ids:
                return True
            if user_id == OWNER_ID:
                return True
            for cid in channel_ids:
                if not await is_sub(client, user_id, cid):
                    mode = await rexbots.get_channel_mode(cid)
                    if mode == "on":
                        await asyncio.sleep(2)
                        if await is_sub(client, user_id, cid):
                            continue
                    return False
            return True
        
        try:
            is_sub_status = await is_subscribed(client, user_id)
            print(f"DEBUG: User {user_id} subscribed status: {is_sub_status}")
            
            if not is_sub_status:
                print(f"DEBUG: User {user_id} is not subscribed, calling not_joined.")
                return await not_joined(client, message)
            
            print(f"DEBUG: User {user_id} is subscribed, proceeding with function call.")
            return await func(client, message, *args, **kwargs)
        
        except Exception as e:
            print(f"FATAL ERROR in check_fsub: {e}")
            await message.reply_text(f"An unexpected error occurred: `{e}`. Please contact the developer.")
            return

    return wrapper
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
async def check_admin(filter, client, update):
    try:
        user_id = update.from_user.id
        return any([user_id == OWNER_ID, await rexbots.admin_exist(user_id)])
    except Exception as e:
        print(f"! Exception in check_admin: {e}")
        return False

async def not_joined(client: Client, message: Message):
    print(f"DEBUG: not_joined function called for user {message.from_user.id}")
    temp = await message.reply("<b><i>ᴡᴀɪᴛ ᴀ sᴇᴄ..</i></b>")

    user_id = message.from_user.id
    buttons = []
    count = 0

    try:
        all_channels = await rexbots.show_channels()
        for chat_id in all_channels:
            mode = await rexbots.get_channel_mode(chat_id)

            await message.reply_chat_action(ChatAction.TYPING)

            # Re-check is_sub status for this logic
            try:
                member = await client.get_chat_member(chat_id, user_id)
                is_member = member.status in {
                    ChatMemberStatus.OWNER,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.MEMBER
                }
            except UserNotParticipant:
                is_member = False
            except Exception as e:
                is_member = False
                print(f"[!] Error checking member in not_joined: {e}")

            if not is_member:
                try:
                    if chat_id in chat_data_cache:
                        data = chat_data_cache[chat_id]
                    else:
                        data = await client.get_chat(chat_id)
                        chat_data_cache[chat_id] = data

                    name = data.title

                    if mode == "on" and not data.username:
                        invite = await client.create_chat_invite_link(
                            chat_id=chat_id,
                            creates_join_request=True,
                            expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                        )
                        link = invite.invite_link
                    else:
                        if data.username:
                            link = f"https://t.me/{data.username}"
                        else:
                            invite = await client.create_chat_invite_link(
                                chat_id=chat_id,
                                expire_date=datetime.utcnow() + timedelta(seconds=FSUB_LINK_EXPIRY) if FSUB_LINK_EXPIRY else None
                            )
                            link = invite.invite_link

                    buttons.append([InlineKeyboardButton(text=name, url=link)])
                    count += 1
                    await temp.edit(f"<b>{'! ' * count}</b>")

                except Exception as e:
                    print(f"Error with chat {chat_id}: {e}")
                    return await temp.edit(
                        f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @EternalsHelplineBot</i></b>\n"
                        f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
                    )

        try:
            buttons.append([
                InlineKeyboardButton(
                    text='• Jᴏɪɴᴇᴅ •',
                    url=f"https://t.me/{Config.BOT_USERNAME}?start=true"
                )
            ])
        except IndexError:
            pass

        text = "<b><blockquote>Hᴇʟʟᴏ!! ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ <a href=https://t.me/AnimeNexusNetwork>ᴀɴɪᴍᴇ ɴᴇxᴜs ɴᴇᴛᴡᴏʀᴋ</a></blockquote>Yᴏᴜ ɴᴇᴇᴅ ᴛᴏ Jᴏɪɴ ɪɴ ᴍʏ Cʜᴀɴɴᴇʟ/Gʀᴏᴜᴘ ғɪʀsᴛ, Pʟᴇᴀsᴇ sᴜʙsᴄʀɪʙᴇ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ ᴀɴᴅ sᴛᴀʀᴛ ʙᴏᴛ ᴀɢᴀɪɴ</b>"
        await temp.delete()
        
        print(f"DEBUG: Sending final reply photo to user {user_id}")
        await message.reply_photo(
            photo=FSUB_PIC,
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    except Exception as e:
        print(f"Final Error: {e}")
        await temp.edit(
            f"<b><i>! Eʀʀᴏʀ, Cᴏɴᴛᴀᴄᴛ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴛᴏ sᴏʟᴠᴇ ᴛʜᴇ ɪssᴜᴇs @EternalsHelplineBot</i></b>\n"
            f"<blockquote expandable><b>Rᴇᴀsᴏɴ:</b> {e}</blockquote>"
        )
        
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

active_sequences = {}
message_ids = {}
renaming_operations = {}
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
def detect_quality(file_name):
    quality_order = {"360p": 0, "480p": 1, "720p": 2, "1080p": 3, "1440p": 4, "2160p": 5, "4k": 6, "Hdrip": 7}
    match = re.search(r"(360p|480p|720p|1080p|1440p|2160p|4k|Hdrip)\b", file_name, re.IGNORECASE)
    return quality_order.get(match.group(1).lower(), 7) if match else 7

# --- Duration Detection Function (from the first bot) ---
async def detect_duration(file_path):
    """Detect the duration of a video or audio file using ffprobe."""
    ffprobe = shutil.which('ffprobe')
    if not ffprobe:
        logger.error("ffprobe not found in PATH")
        raise RuntimeError("ffprobe not found in PATH")

    cmd = [
        ffprobe,
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        file_path
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()

    try:
        info = json.loads(stdout)
        format_info = info.get('format', {})
        duration = float(format_info.get('duration', 0))
        return duration
    except Exception as e:
        logger.error(f"Duration detection error: {e}")
        return 0

# --- REVISED extract_episode_number ---
def extract_episode_number(filename):
    if not filename:
        return None

    print(f"DEBUG: Extracting episode from: '{filename}')")

    quality_and_year_indicators = [
        r'\d{2,4}[pP]',
        r'\dK',
        r'HD(?:RIP)?',
        r'WEB(?:-)?DL',
        r'BLURAY',
        r'X264',
        r'X265',
        r'HEVC',
        r'FHD',
        r'UHD',
        r'HDR',
        r'H\.264', r'H\.265',
        r'(?:19|20)\d{2}',
        r'MULTI(?:audio)?',
        r'DUAL(?:audio)?',
    ]
    quality_pattern_for_exclusion = r'(?:' + '|'.join([f'(?:[\\s._-]*{ind})' for ind in quality_and_year_indicators]) + r')'

    patterns = [
        re.compile(r'S\d+[.-_]?E(\d+)', re.IGNORECASE),
        re.compile(r'(?:Episode|EP)[\s._-]*(\d+)', re.IGNORECASE),
        re.compile(r'\bE(\d+)\b', re.IGNORECASE),
        re.compile(r'[\[\(]E(\d+)[\]\)]', re.IGNORECASE),
        re.compile(r'\b(\d+)\s*of\s*\d+\b', re.IGNORECASE),

        re.compile(
            r'(?:^|[^0-9A-Z])'
            r'(\d{1,4})'
            r'(?:[^0-9A-Z]|$)'
            r'(?!' + quality_pattern_for_exclusion + r')'
            , re.IGNORECASE
        ),
    ]

    for i, pattern in enumerate(patterns):
        matches = pattern.findall(filename)
        if matches:
            for match in matches:
                try:
                    if isinstance(match, tuple):
                        episode_str = match[0]
                    else:
                        episode_str = match

                    episode_num = int(episode_str)

                    if 1 <= episode_num <= 9999:
                        if episode_num in [360, 480, 720, 1080, 1440, 2160, 2020, 2021, 2022, 2023, 2024, 2025]:
                            if re.search(r'\b' + str(episode_num) + r'(?:p|K|HD|WEB|BLURAY|X264|X265|HEVC|MULTI|DUAL)\b', filename, re.IGNORECASE) or \
                                re.search(r'\b(?:19|20)\d{2}\b', filename, re.IGNORECASE) and len(str(episode_num)) == 4:
                                print(f"DEBUG: Skipping {episode_num} as it is a common quality/year number.")
                                continue

                        print(f"DEBUG: Episode Pattern {i+1} found episode: {episode_num}")
                        return episode_num
                except ValueError:
                    continue

    print(f"DEBUG: No episode number found in: '{filename}'")
    return None
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
# --- MODIFIED: extract_season_number (added negative lookahead) ---
def extract_season_number(filename):
    if not filename:
        return None

    print(f"DEBUG: Extracting season from: '{filename}')")

    quality_and_year_indicators = [
        r'\d{2,4}[pP]',
        r'\dK',
        r'HD(?:RIP)?',
        r'WEB(?:-)?DL',
        r'BLURAY',
        r'X264',
        r'X265',
        r'HEVC',
        r'FHD',
        r'UHD',
        r'HDR',
        r'H\.264', r'H\.265',
        r'(?:19|20)\d{2}',
        r'MULTI(?:audio)?',
        r'DUAL(?:audio)?',
    ]
    quality_pattern_for_exclusion = r'(?:' + '|'.join([f'(?:[\\s._-]*{ind})' for ind in quality_and_year_indicators]) + r')'


    patterns = [
        re.compile(r'S(\d+)[._-]?E\d+', re.IGNORECASE),

        re.compile(r'(?:Season|SEASON|season)[\s._-]*(\d+)', re.IGNORECASE),

        re.compile(r'\bS(\d+)\b(?!E\d|' + quality_pattern_for_exclusion + r')', re.IGNORECASE),

        re.compile(r'[\[\(]S(\d+)[\]\)]', re.IGNORECASE),

        re.compile(r'[._-]S(\d+)(?:[._-]|$)', re.IGNORECASE),

        re.compile(r'(?:season|SEASON|Season)[\s._-]*(\d+)', re.IGNORECASE),

        re.compile(r'(?:^|[\s._-])(?:season|SEASON|Season)[\s._-]*(\d+)(?:[\s._-]|$)', re.IGNORECASE),

        re.compile(r'[\[\(](?:season|SEASON|Season)[\s._-]*(\d+)[\]\)]', re.IGNORECASE),

        re.compile(r'(?:season|SEASON|Season)[._\s-]+(\d+)', re.IGNORECASE),

        re.compile(r'(?:^season|season$)[\s._-]*(\d+)', re.IGNORECASE),
    ]

    for i, pattern in enumerate(patterns):
        match = pattern.search(filename)
        if match:
            try:
                season_num = int(match.group(1))
                if 1 <= season_num <= 99:
                    print(f"DEBUG: Season Pattern {i+1} found season: {season_num}")
                    return season_num
            except ValueError:
                continue

    print(f"DEBUG: No season number found in: '{filename}'")
    return None
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
def extract_audio_info(filename):
    """Extract audio information from filename, including languages and 'dual'/'multi'."""
    audio_keywords = {
        'Hindi': re.compile(r'Hindi', re.IGNORECASE),
        'English': re.compile(r'English', re.IGNORECASE),
        'Multi': re.compile(r'Multi(?:audio)?', re.IGNORECASE),
        'Telugu': re.compile(r'Telugu', re.IGNORECASE),
        'Eng': re.compile(r'Eng', re.IGNORECASE),
        'Sub': re.compile(r'Sub', re.IGNORECASE),
        'Eng sub': re.compile(r'Eng sub', re.IGNORECASE),
        'Dub': re.compile(r'Dub', re.IGNORECASE),
        'Eng dub': re.compile(r'Eng dub', re.IGNORECASE),
        'Tamil': re.compile(r'Tamil', re.IGNORECASE),
        'Jap': re.compile(r'Jap', re.IGNORECASE),
        'Dual': re.compile(r'Dual(?:audio)?', re.IGNORECASE),
        'Dual_Enhanced': re.compile(r'(?:DUAL(?:[\s._-]?AUDIO)?|\[DUAL\])', re.IGNORECASE),
        'AAC': re.compile(r'AAC', re.IGNORECASE),
        'AC3': re.compile(r'AC3', re.IGNORECASE),
        'DTS': re.compile(r'DTS', re.IGNORECASE),
        'MP3': re.compile(r'MP3', re.IGNORECASE),
        '5.1': re.compile(r'5\.1', re.IGNORECASE),
        '2.0': re.compile(r'2\.0', re.IGNORECASE),
    }

    detected_audio = []

    if re.search(r'\bMulti(?:audio)?\b', filename, re.IGNORECASE):
        detected_audio.append("Multi")
    if re.search(r'\bDual(?:audio)?\b', filename, re.IGNORECASE):
        detected_audio.append("Dual")


    priority_keywords = ['Hindi', 'English', 'Telugu', 'Tamil', 'Eng', 'Sub', 'Eng sub', 'Dub', 'Eng dub', 'Jap']
    for keyword in priority_keywords:
        if audio_keywords[keyword].search(filename):
            if keyword not in detected_audio:
                detected_audio.append(keyword)

    for keyword in ['AAC', 'AC3', 'DTS', 'MP3', '5.1', '2.0']:
        if audio_keywords[keyword].search(filename):
            if keyword not in detected_audio:
                detected_audio.append(keyword)

    detected_audio = list(dict.fromkeys(detected_audio))

    if detected_audio:
        return ' '.join(detected_audio)

    return None
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
def extract_quality(filename):
    """Extract video quality from filename."""
    patterns = [
        re.compile(r'\b(Hdrip|4K|2K|2160p|1440p|1080p|720p|480p|360p)\b', re.IGNORECASE),
        re.compile(r'\b(HD(?:RIP)?|WEB(?:-)?DL|BLURAY)\b', re.IGNORECASE),
        re.compile(r'\b(X264|X265|HEVC)\b', re.IGNORECASE),
    ]

    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            found_quality = match.group(1)
            if found_quality.lower() in ["4k", "2k", "hdrip", "web-dl", "bluray"]:
                return found_quality.upper() if found_quality.upper() in ["4K", "2K"] else found_quality.capitalize()
            return found_quality

    return None

@Client.on_message(filters.command("start_sequence") & filters.private)
@check_ban
@check_fsub
async def start_sequence(client, message: Message):
    user_id = message.from_user.id
    if user_id in active_sequences:
        await message.reply_text("Hᴇʏ ᴅᴜᴅᴇ...!! A sᴇǫᴜᴇɴᴄᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ! Usᴇ /end_sequence ᴛᴏ ᴇɴᴅ ɪᴛ.")
    else:
        active_sequences[user_id] = []
        message_ids[user_id] = []
        msg = await message.reply_text("Sᴇǫᴜᴇɴᴄᴇ sᴛᴀʀᴛᴇᴅ! Sᴇɴᴅ ʏᴏᴜʀ ғɪʟᴇs ɴᴏᴡ ʙʀᴏ....Fᴀsᴛ")
        message_ids[user_id].append(msg.id)

@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
@check_ban
@check_verification
@check_fsub
async def auto_rename_files(client, message):
    """Main handler for auto-renaming files"""
    async with _get_semaphore():
        # Initialize variables at the start to avoid UnboundLocalError
        msg = None 
        download_path = None
        metadata_path = None
        output_path = None
        input_path = None
        
        try:
            user_id = message.from_user.id
            user = message.from_user
            format_template = await rexbots.get_format_template(user_id)
            media_preference = await rexbots.get_media_preference(user_id)
        
            if not format_template:
                await message.reply_text("Pʟᴇᴀsᴇ Sᴇᴛ Aɴ Aᴜᴛᴏ Rᴇɴᴀᴍᴇ Fᴏʀᴍᴀᴛ Fɪʀsᴛ Usɪɴɢ /autorename")
                return
        
            # Correctly identify file properties and initial media type
            if message.document:
                file_id = message.document.file_id
                file_name = message.document.file_name
                file_size = message.document.file_size
                media_type = "document"
            elif message.video:
                file_id = message.video.file_id
                file_name = message.video.file_name or "video"
                file_size = message.video.file_size
                media_type = "video"
            elif message.audio:
                file_id = message.audio.file_id
                file_name = message.audio.file_name or "audio"
                file_size = message.audio.file_size
                media_type = "audio"
            else:
                return await message.reply_text("Unsupported file type")
                
            if not file_name:
                await message.reply_text("Could not determine file name.")
                return

            if file_id in renaming_operations:
                if (datetime.now() - renaming_operations[file_id]).seconds < 10:
                    return
            renaming_operations[file_id] = datetime.now()
                    
            file_info = {
                "file_id": file_id,
                "file_name": file_name,
                "message": message,
                "episode_num": extract_episode_number(file_name)
            }

            if user_id in active_sequences:
                active_sequences[user_id].append(file_info)
                reply_msg = await message.reply_text("Wᴇᴡ...ғɪʟᴇs ʀᴇᴄᴇɪᴠᴇᴅ ɴᴏᴡ ᴜsᴇ /end_sequence ᴛᴏ ɢᴇᴛ ʏᴏᴜʀ ғɪʟᴇs...!!")
                message_ids[user_id].append(reply_msg.id)
                return

            if media_preference:
                media_type = media_preference
            else:
                # Fallback to intelligent guessing if no preference is set
                if file_name.endswith((".mp4", ".mkv", ".avi", ".webm")):
                    media_type = "document"
                elif file_name.endswith((".mp3", ".flac", ".wav", ".ogg")):
                    media_type = "audio"
                else:
                    media_type = "video"

            episode_number = extract_episode_number(file_name)
            season_number = extract_season_number(file_name)
            audio_info_extracted = extract_audio_info(file_name)
            quality_extracted = extract_quality(file_name)

            print(f"DEBUG: Final extracted values - Season: {season_number}, Episode: {episode_number}, Quality: {quality_extracted}, Audio: {audio_info_extracted}")

            season_value_formatted = str(season_number).zfill(2) if season_number is not None else "01"
            episode_value_formatted = str(episode_number).zfill(2) if episode_number is not None else "01"

            template = re.sub(r'S(?:Season|season|SEASON)(\d+)', f'S{season_value_formatted}', format_template, flags=re.IGNORECASE)

            season_replacements = [
                (re.compile(r'\{season\}', re.IGNORECASE), season_value_formatted),
                (re.compile(r'\{Season\}', re.IGNORECASE), season_value_formatted),
                (re.compile(r'\{SEASON\}', re.IGNORECASE), season_value_formatted),
                (re.compile(r'\bseason\b', re.IGNORECASE), season_value_formatted),
                (re.compile(r'\bSeason\b', re.IGNORECASE), season_value_formatted),
                (re.compile(r'\bSEASON\b', re.IGNORECASE), season_value_formatted),
                (re.compile(r'Season[\s._-]*\d*', re.IGNORECASE), season_value_formatted),
                (re.compile(r'season[\s._-]*\d*', re.IGNORECASE), season_value_formatted),
                (re.compile(r'SEASON[\s._-]*\d*', re.IGNORECASE), season_value_formatted),
            ]

            for pattern, replacement in season_replacements:
                template = pattern.sub(replacement, template)
                    
            template = re.sub(r'EP(?:Episode|episode|EPISODE)', f'EP{episode_value_formatted}', template, flags=re.IGNORECASE)

            episode_patterns = [
                re.compile(r'\{episode\}', re.IGNORECASE),
                re.compile(r'\bEpisode\b', re.IGNORECASE),
                re.compile(r'\bEP\b', re.IGNORECASE)
            ]

            for pattern in episode_patterns:
                template = pattern.sub(episode_value_formatted, template)

            audio_replacement = audio_info_extracted if audio_info_extracted else ""
            audio_patterns = [
                re.compile(r'\{audio\}', re.IGNORECASE),
                re.compile(r'\bAudio\b', re.IGNORECASE),
            ]

            for pattern in audio_patterns:
                template = pattern.sub(audio_replacement, template)

            quality_replacement = quality_extracted if quality_extracted else ""
            quality_patterns = [
                re.compile(r'\{quality\}', re.IGNORECASE),
                re.compile(r'\bQuality\b', re.IGNORECASE),
            ]

            for pattern in quality_patterns:
                template = pattern.sub(quality_replacement, template)

            # {name} = first 3 letters of original filename (without extension)
            original_base = os.path.splitext(file_name)[0] if file_name else ""
            # Keep only alphanumeric for a clean short name
            clean_base = re.sub(r'[^A-Za-z0-9]', '', original_base)
            name_short = (clean_base[:3] if clean_base else "FIL").upper()
            name_patterns = [
                re.compile(r'\{name\}', re.IGNORECASE),
                re.compile(r'\{NAME\}', re.IGNORECASE),
            ]
            for pattern in name_patterns:
                template = pattern.sub(name_short, template)

            template = re.sub(r'\[\s*\]', '', template)
            template = re.sub(r'\(\s*\)', '', template)
            template = re.sub(r'\{\s*\}', '', template)

            # Sanitize template / filename so it can never become an absolute path
            # or contain path separators (os.path.join treats leading / as absolute)
            template = template.strip()
            template = template.lstrip('/\\')                    # remove leading slashes
            template = re.sub(r'[/\\]+', '_', template)          # replace remaining path seps
            template = re.sub(r'[<>:"|?*\x00-\x1f]', '', template)  # remove illegal filename chars
            template = template.strip('. ')                      # no leading/trailing dots/spaces
            if not template:
                template = "renamed_file"

            _, file_extension = os.path.splitext(file_name)
            file_extension = (file_extension or '').lower()

            # ---- File category & target extension ----
            VIDEO_EXTS = {
                '.mp4', '.m4v', '.mkv', '.avi', '.webm', '.mov', '.flv',
                '.wmv', '.ts', '.m2ts', '.mpeg', '.mpg', '.3gp', '.vob', '.mts'
            }
            AUDIO_EXTS = {
                '.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac', '.opus', '.wma', '.ape'
            }
            IMAGE_EXTS = {
                '.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif'
            }
            # Music stored as .mp4 (common) is treated as audio when Telegram sent it as audio
            is_video_file = file_extension in VIDEO_EXTS or media_type == "video"
            is_audio_file = file_extension in AUDIO_EXTS or media_type == "audio"
            is_image_file = file_extension in IMAGE_EXTS
            is_pdf_file = file_extension == '.pdf'

            # Target extension rules:
            # 1) Any video → .mkv
            # 2) Images & text documents → .pdf
            # 3) Music / audio → keep original (music .mp4 → .m4a)
            # 4) Already PDF → .pdf
            # 5) Other documents (docx, zip, etc.) → keep original extension
            TEXT_DOC_EXTS = {'.txt', '.md', '.csv', '.log', '.json', '.xml', '.html', '.htm'}
            if is_video_file and not is_audio_file:
                final_extension = ".mkv"
                convert_kind = "video_mkv"
            elif is_audio_file or (file_extension == '.mp4' and media_type == "audio"):
                # music .mp4 → remux to .m4a for proper audio container
                if file_extension in ('.mp4', '.m4v'):
                    final_extension = ".m4a"
                    convert_kind = "audio_m4a"
                else:
                    final_extension = file_extension or ".mp3"
                    convert_kind = "audio_keep"
            elif is_image_file:
                final_extension = ".pdf"
                convert_kind = "image_pdf"
            elif file_extension in TEXT_DOC_EXTS:
                final_extension = ".pdf"
                convert_kind = "doc_pdf"
            elif is_pdf_file:
                final_extension = ".pdf"
                convert_kind = "pdf_keep"
            else:
                # Unknown / office docs / archives → keep original
                final_extension = file_extension if file_extension else ".bin"
                convert_kind = "keep"

            if not final_extension.startswith('.'):
                final_extension = '.' + final_extension

            # Avoid double extensions (e.g. .mkv.mkv) if template already ends with one
            template_base, template_ext = os.path.splitext(template)
            if template_ext.lower() == final_extension.lower():
                new_file_name = f"{template_base}{final_extension}"
            else:
                new_file_name = f"{template}{final_extension}"

            user_folder = str(user_id)
            # Download with ORIGINAL extension so ffmpeg/pillow can detect format
            download_name = f"{template_base or 'file'}{file_extension or ''}"
            download_path = os.path.join("downloads", user_folder, download_name)
            metadata_path = os.path.join("metadata", user_folder, new_file_name)
            output_path = os.path.join("processed", user_folder, new_file_name)

            # Extra safety: never allow absolute paths
            for p in (download_path, metadata_path, output_path):
                if os.path.isabs(p):
                    raise RuntimeError(f"Invalid path generated (absolute): {p}")

            # Create user-specific directories
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            msg = await message.reply_text("Wᴇᴡ... Iᴀm ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...!!")
            await message.reply_chat_action(ChatAction.PLAYING)

            try:
                file_path = await client.download_media(
                    message,
                    file_name=download_path,
                    progress=progress_for_pyrogram,
                    progress_args=("Dᴏᴡɴʟᴏᴀᴅ sᴛᴀʀᴛᴇᴅ ᴅᴜᴅᴇ...!!", msg, time.time())
                )
            except Exception as e:
                await msg.edit(f"Dᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ: {e}")
                raise

            # Check whether user wants metadata applied
            metadata_enabled = (await rexbots.get_metadata(user_id)) == "On"

            # ---- Conversion step ----
            try:
                if convert_kind == "video_mkv":
                    await msg.edit("Vɪᴅᴇᴏ ᴅᴇᴛᴇᴄᴛᴇᴅ. Cᴏɴᴠᴇʀᴛɪɴɢ ᴛᴏ MKV...")
                    await message.reply_chat_action(ChatAction.PLAYING)
                    await convert_to_mkv(file_path, metadata_path, user_id, apply_metadata=metadata_enabled)
                    file_path = metadata_path
                elif convert_kind == "audio_m4a":
                    await msg.edit("Mᴜsɪᴄ MP4 ᴅᴇᴛᴇᴄᴛᴇᴅ. Cᴏɴᴠᴇʀᴛɪɴɢ ᴛᴏ M4A...")
                    await message.reply_chat_action(ChatAction.PLAYING)
                    await convert_to_m4a(file_path, metadata_path, user_id, apply_metadata=metadata_enabled)
                    file_path = metadata_path
                elif convert_kind in ("image_pdf", "doc_pdf"):
                    await msg.edit("Dᴏᴄᴜᴍᴇɴᴛ/Iᴍᴀɢᴇ ᴅᴇᴛᴇᴄᴛᴇᴅ. Cᴏɴᴠᴇʀᴛɪɴɢ ᴛᴏ PDF...")
                    await message.reply_chat_action(ChatAction.PLAYING)
                    await convert_to_pdf(file_path, metadata_path)
                    file_path = metadata_path
                elif convert_kind == "pdf_keep":
                    # Optional metadata pass for PDF is not supported via ffmpeg the same way;
                    # just copy so paths stay consistent
                    if file_path != metadata_path:
                        shutil.copy2(file_path, metadata_path)
                        file_path = metadata_path
                elif convert_kind in ("audio_keep", "keep"):
                    # Metadata only when enabled (ffmpeg works for many audio containers)
                    if metadata_enabled and convert_kind == "audio_keep":
                        await msg.edit("Nᴏᴡ ᴀᴅᴅɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴅᴜᴅᴇ...!!")
                        await message.reply_chat_action(ChatAction.PLAYING)
                        try:
                            await add_metadata(file_path, metadata_path, user_id)
                            file_path = metadata_path
                        except Exception as e:
                            logger.error(f"Failed to add metadata: {e}")
                    elif file_path != metadata_path and convert_kind == "keep":
                        # No conversion needed; copy for consistent cleanup paths
                        try:
                            shutil.copy2(file_path, metadata_path)
                            file_path = metadata_path
                        except Exception:
                            pass
                else:
                    # Fallback: metadata only if enabled and not already converted
                    if metadata_enabled:
                        await msg.edit("Nᴏᴡ ᴀᴅᴅɪɴɢ ᴍᴇᴛᴀᴅᴀᴛᴀ ᴅᴜᴅᴇ...!!")
                        await message.reply_chat_action(ChatAction.PLAYING)
                        try:
                            await add_metadata(file_path, metadata_path, user_id)
                            file_path = metadata_path
                        except Exception as e:
                            logger.error(f"Failed to add metadata: {e}")
            except Exception as e:
                await msg.edit(f"❌ Eʀʀᴏʀ ᴅᴜʀɪɴɢ ᴄᴏɴᴠᴇʀsɪᴏɴ: {str(e)}")
                return

            # Detect duration for video or audio files
            duration = 0
            if convert_kind in ("video_mkv", "audio_m4a", "audio_keep") or media_type in ("video", "audio"):
                try:
                    duration = await detect_duration(file_path)
                except Exception as e:
                    logger.error(f"Failed to detect duration: {e}")
                    duration = 0
            human_readable_duration = convert(duration) if duration > 0 else "N/A"

            # Adjust media_type for upload based on what we produced
            if convert_kind == "video_mkv":
                # Prefer user's media preference; default to document for mkv (better for large files)
                if media_preference in ("video", "document"):
                    media_type = media_preference
                else:
                    media_type = "document"
            elif convert_kind in ("audio_m4a", "audio_keep"):
                media_type = "audio"
            elif convert_kind in ("image_pdf", "doc_pdf", "pdf_keep"):
                media_type = "document"

            await msg.edit("Wᴇᴡ... Iᴀm Uᴘʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...!!")
            await message.reply_chat_action(ChatAction.PLAYING)
            
            try:
                await rexbots.col.update_one(
                    {"_id": user_id},
                    {
                        "$inc": {"rename_count": 1},
                        "$set": {
                            "first_name": message.from_user.first_name,
                            "username": message.from_user.username,
                            "last_activity_timestamp": datetime.now()
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Failed to update database: {e}")

            c_caption = await rexbots.get_caption(message.chat.id)
            
            if c_caption:
                try:
                    caption = c_caption.format(
                        filename=new_file_name,
                        filesize=humanbytes(file_size),
                        duration=human_readable_duration
                    )
                except (KeyError, ValueError, IndexError):
                    # Fallback if user caption template has invalid placeholders
                    caption = f"**{new_file_name}**"
            else:
                caption = f"**{new_file_name}**"
                
            c_thumb = await rexbots.get_thumbnail(message.chat.id)

            ph_path = None
            if c_thumb:
                ph_path = await client.download_media(c_thumb)
            elif media_type == "video" and message.video and message.video.thumbs:
                try:
                    ph_path = await client.download_media(message.video.thumbs[0].file_id)
                except IndexError:
                    ph_path = None

            if ph_path:
                try:
                    img = Image.open(ph_path).convert("RGB")
                    img.save(ph_path, "JPEG")
                except Exception as e:
                    logger.error(f"Failed to process video thumbnail: {e}")
                    ph_path = None

            # Define common upload parameters
            # Explicit file_name ensures both the Telegram file name AND caption show the new name
            common_upload_params = {
                'chat_id': message.chat.id,
                'caption': caption,
                'thumb': ph_path,
                'file_name': new_file_name,
                'progress': progress_for_pyrogram,
                'progress_args': ("Uᴘʟᴏᴀᴅ sᴛᴀʀᴛᴇᴅ ᴅᴜᴅᴇ...!!", msg, time.time())
            }

            sent_message = None
            if media_type == "document":
                sent_message = await client.send_document(document=file_path, **common_upload_params)
            elif media_type == "video":
                if duration > 0:
                    common_upload_params['duration'] = int(duration)
                sent_message = await client.send_video(video=file_path, **common_upload_params)
            elif media_type == "audio":
                if duration > 0:
                    common_upload_params['duration'] = int(duration)
                sent_message = await client.send_audio(audio=file_path, **common_upload_params)

                    
            await msg.delete()

        except Exception as e:
            err_text = f"❌ Eʀʀᴏʀ ᴅᴜʀɪɴɢ ʀᴇɴᴀᴍɪɴɢ: {str(e)}"
            try:
                if msg:
                    await msg.edit(err_text)
                else:
                    await message.reply_text(err_text)
            except Exception:
                pass
            raise
        finally:
            # Clean up files
            for path in [download_path, metadata_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"Error removing file {path}: {e}")
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
@Client.on_message(filters.command("showformat") & filters.private)
@check_ban
@check_fsub
async def show_format_cmd(client, message: Message):
    """Shows the user their currently set auto-rename format."""
    user_id = message.from_user.id
    
    # 1. Fetch the format template from the database
    # This calls the same function used in your auto_rename_files handler
    try:
        format_template = await rexbots.get_format_template(user_id)
    except Exception as e:
        # Handle potential database errors (optional but recommended)
        await message.reply_text(f"❌ Eʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ғᴏʀᴍᴀᴛ: {e}")
        return

    # 2. Check if a format was found
    if format_template:
        response_text = (
            f"✨ Yᴏᴜʀ ᴄᴜʀʀᴇɴᴛ Aᴜᴛᴏ Rᴇɴᴀᴍᴇ Fᴏʀᴍᴀᴛ ɪs:\n\n"
            f"/autorename `{format_template}`\n\n"
            "Uꜱᴇ /autorename ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛ."
        )
    else:
        response_text = (
            "⚠️ Yᴏᴜ ʜᴀᴠᴇ ɴᴏᴛ ꜱᴇᴛ ᴀɴ Aᴜᴛᴏ Rᴇɴᴀᴍᴇ Fᴏʀᴍᴀᴛ ʏᴇᴛ.\n"
            "Pʟᴇᴀꜱᴇ ꜱᴇᴛ ᴏɴᴇ ᴜꜱɪɴɢ /autorename."
        )

    # 3. Send the response
    await message.reply_text(response_text)
# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------
@Client.on_message(filters.command("end_sequence") & filters.private)
@check_ban
@check_fsub
async def end_sequence(client, message: Message):
    user_id = message.from_user.id
    if user_id not in active_sequences:
        await message.reply_text("Wʜᴀᴛ ᴀʀᴇ ʏᴏᴜ ᴅᴏɪɴɢ ɴᴏ ᴀᴄᴛɪᴠᴇ sᴇǫᴜᴇɴᴄᴇ ғᴏᴜɴᴅ...!!")
    else:
        file_list = active_sequences.pop(user_id, [])
        delete_messages = message_ids.pop(user_id, [])
        count = len(file_list)

        if not file_list:
            await message.reply_text("Nᴏ ғɪʟᴇs ᴡᴇʀᴇ sᴇɴᴛ ɪɴ ᴛʜɪs sᴇǫᴜᴇɴᴄᴇ....ʙʀᴏ...!!")
        else:
            file_list.sort(key=lambda x: x["episode_num"] if x["episode_num"] is not None else float('inf'))
            await message.reply_text(f"Sᴇǫᴜᴇɴᴄᴇ ᴇɴᴅᴇᴅ. Nᴏᴡ sᴇɴᴅɪɴɢ ʏᴏᴜʀ {count} ғɪʟe(s) ʙᴀᴄᴋ ɪɴ sᴇǫᴜᴇɴᴄᴇ...!!")

            for index, file_info in enumerate(file_list, 1):
                try:
                    await asyncio.sleep(0.5)

                    original_message = file_info["message"]

                    if original_message.document:
                        await client.send_document(
                            message.chat.id,
                            original_message.document.file_id,
                            caption=f"{file_info['file_name']}"
                        )
                    elif original_message.video:
                        await client.send_video(
                            message.chat.id,
                            original_message.video.file_id,
                            caption=f"{file_info['file_name']}"
                        )
                    elif original_message.audio:
                        await client.send_audio(
                            message.chat.id,
                            original_message.audio.file_id,
                            caption=f"{file_info['file_name']}"
                        )
                except Exception as e:
                    await message.reply_text(f"Fᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ғɪʟᴇ: {file_info.get('file_name', '')}\n{e}")

            await message.reply_text(f"✅ Aʟʟ {count} ғɪʟes sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ɪɴ sᴇǫᴜᴇɴᴄᴇ!")

        try:
            await client.delete_messages(chat_id=message.chat.id, message_ids=delete_messages)
        except Exception as e:
            print(f"Error deleting messages: {e}")

async def add_metadata(input_path, output_path, user_id):
    ffmpeg_cmd = shutil.which('ffmpeg')
    if not ffmpeg_cmd:
        raise RuntimeError("FFmpeg not found in PATH")

    # Guard against accidental in-place edit (FFmpeg forbids same input/output)
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise RuntimeError(
            f"Input and output paths are identical ({input_path}). "
            "This usually means the rename template produced an absolute path."
        )

    metadata_command = [
        ffmpeg_cmd,
        '-i', input_path,
        '-metadata', f'title={await rexbots.get_title(user_id)}',
        '-metadata', f'artist={await rexbots.get_artist(user_id)}',
        '-metadata', f'author={await rexbots.get_author(user_id)}',
        '-metadata:s:v', f'title={await rexbots.get_video(user_id)}',
        '-metadata:s:a', f'title={await rexbots.get_audio(user_id)}',
        '-metadata:s:s', f'title={await rexbots.get_subtitle(user_id)}',
        '-metadata', f'encoded_by={await rexbots.get_encoded_by(user_id)}',
        '-metadata', f'custom_tag={await rexbots.get_custom_tag(user_id)}',
        '-map', '0',
        '-c', 'copy',
        '-loglevel', 'error',
        '-y',
        output_path
    ]

    process = await asyncio.create_subprocess_exec(
        *metadata_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {stderr.decode()}")

async def convert_to_mkv(input_path, output_path, user_id, apply_metadata=True):
    """Convert video file to MKV format (stream copy). Optionally apply metadata tags."""
    ffmpeg_cmd = shutil.which('ffmpeg')
    if not ffmpeg_cmd:
        raise RuntimeError("FFmpeg not found in PATH")

    # Guard against accidental in-place edit (FFmpeg forbids same input/output)
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise RuntimeError(
            f"Input and output paths are identical ({input_path}). "
            "This usually means the rename template produced an absolute path."
        )

    cmd = [
        ffmpeg_cmd,
        '-hide_banner',
        '-i', input_path,
    ]

    if apply_metadata:
        cmd.extend([
            '-metadata', f'title={await rexbots.get_title(user_id)}',
            '-metadata', f'artist={await rexbots.get_artist(user_id)}',
            '-metadata', f'author={await rexbots.get_author(user_id)}',
            '-metadata:s:v', f'title={await rexbots.get_video(user_id)}',
            '-metadata:s:a', f'title={await rexbots.get_audio(user_id)}',
            '-metadata:s:s', f'title={await rexbots.get_subtitle(user_id)}',
            '-metadata', f'encoded_by={await rexbots.get_encoded_by(user_id)}',
            '-metadata', f'custom_tag={await rexbots.get_custom_tag(user_id)}',
        ])

    cmd.extend([
        '-map', '0',
        '-c', 'copy',
        '-f', 'matroska',
        '-y',
        output_path
    ])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        raise RuntimeError(f"MKV conversion failed: {error_msg}")


async def convert_to_m4a(input_path, output_path, user_id, apply_metadata=True):
    """Remux music/video-in-mp4 to M4A audio container (stream copy when possible)."""
    ffmpeg_cmd = shutil.which('ffmpeg')
    if not ffmpeg_cmd:
        raise RuntimeError("FFmpeg not found in PATH")

    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise RuntimeError(
            f"Input and output paths are identical ({input_path}). "
            "This usually means the rename template produced an absolute path."
        )

    cmd = [
        ffmpeg_cmd,
        '-hide_banner',
        '-i', input_path,
        '-vn',                 # drop video track if present
        '-map', '0:a:0?',
        '-c:a', 'copy',
    ]

    if apply_metadata:
        cmd.extend([
            '-metadata', f'title={await rexbots.get_title(user_id)}',
            '-metadata', f'artist={await rexbots.get_artist(user_id)}',
            '-metadata', f'author={await rexbots.get_author(user_id)}',
            '-metadata', f'encoded_by={await rexbots.get_encoded_by(user_id)}',
            '-metadata', f'custom_tag={await rexbots.get_custom_tag(user_id)}',
        ])

    cmd.extend(['-y', output_path])

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await process.communicate()

    if process.returncode != 0:
        # Fallback: re-encode to AAC if stream copy fails
        cmd_fallback = [
            ffmpeg_cmd, '-hide_banner', '-i', input_path,
            '-vn', '-map', '0:a:0?',
            '-c:a', 'aac', '-b:a', '192k',
            '-y', output_path
        ]
        process2 = await asyncio.create_subprocess_exec(
            *cmd_fallback,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        _, stderr2 = await process2.communicate()
        if process2.returncode != 0:
            raise RuntimeError(f"M4A conversion failed: {stderr2.decode().strip()}")


async def convert_to_pdf(input_path, output_path):
    """
    Convert image (or simple text) files to PDF using Pillow.
    Non-image documents that Pillow cannot open are copied as-is only if already PDF;
    otherwise a minimal PDF is created from available content when possible.
    """
    if os.path.abspath(input_path) == os.path.abspath(output_path):
        raise RuntimeError(
            f"Input and output paths are identical ({input_path})."
        )

    ext = os.path.splitext(input_path)[1].lower()

    # Already PDF → just copy
    if ext == '.pdf':
        shutil.copy2(input_path, output_path)
        return

    # Images → RGB PDF via Pillow
    image_exts = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tiff', '.tif'}
    if ext in image_exts:
        try:
            img = Image.open(input_path)
            # Handle multi-frame (GIF/TIFF) – take first frame for simplicity
            if getattr(img, 'is_animated', False) or getattr(img, 'n_frames', 1) > 1:
                img.seek(0)
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'PDF', resolution=100.0)
            return
        except Exception as e:
            raise RuntimeError(f"Image→PDF conversion failed: {e}")

    # Plain text → simple multi-page PDF using Pillow
    text_exts = {'.txt', '.md', '.csv', '.log', '.json', '.xml', '.html', '.htm'}
    if ext in text_exts:
        try:
            with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
                text = f.read()
            # Render text onto white pages
            from PIL import ImageDraw, ImageFont
            page_w, page_h = 595, 842  # A4-ish at 72dpi
            margin = 40
            line_h = 14
            try:
                font = ImageFont.load_default()
            except Exception:
                font = None

            lines = []
            for paragraph in text.splitlines() or ['']:
                # crude wrap
                words = paragraph.split(' ')
                current = ''
                for w in words:
                    test = (current + ' ' + w).strip()
                    if font and hasattr(font, 'getlength'):
                        too_long = font.getlength(test) > (page_w - 2 * margin)
                    else:
                        too_long = len(test) > 90
                    if too_long and current:
                        lines.append(current)
                        current = w
                    else:
                        current = test
                lines.append(current)

            pages = []
            y = margin
            page = Image.new('RGB', (page_w, page_h), 'white')
            draw = ImageDraw.Draw(page)
            for line in lines:
                if y + line_h > page_h - margin:
                    pages.append(page)
                    page = Image.new('RGB', (page_w, page_h), 'white')
                    draw = ImageDraw.Draw(page)
                    y = margin
                draw.text((margin, y), line[:200], fill='black', font=font)
                y += line_h
            pages.append(page)

            if len(pages) == 1:
                pages[0].save(output_path, 'PDF', resolution=100.0)
            else:
                pages[0].save(output_path, 'PDF', resolution=100.0, save_all=True, append_images=pages[1:])
            return
        except Exception as e:
            raise RuntimeError(f"Text→PDF conversion failed: {e}")

    # Unsupported document type for PDF conversion
    raise RuntimeError(
        f"Cannot convert '{ext}' to PDF. Supported: images ({', '.join(sorted(image_exts))}) "
        f"and text files ({', '.join(sorted(text_exts))})."
    )


# ----------------------------------------
# 𝐌𝐀𝐃𝐄 𝐁𝐘 𝐀𝐁𝐇𝐈
# 𝐓𝐆 𝐈𝐃 : @𝐂𝐋𝐔𝐓𝐂𝐇𝟎𝟎𝟖
# 𝐀𝐍𝐘 𝐈𝐒𝐒𝐔𝐄𝐒 𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐎𝐑𝐄 𝐓𝐇𝐈𝐍𝐆𝐬 𝐂𝐀𝐍 𝐂𝐎𝐍𝐓𝐀𝐂𝐓 𝐌𝐄
# ----------------------------------------

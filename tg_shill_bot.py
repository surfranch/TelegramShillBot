import asyncio
import functools
import math
import random
import sys
from datetime import datetime

import asyncstdlib
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import FloodWaitError, SlowModeWaitError

import yaml

with open("settings.yml", "r", encoding="utf8") as settings:
    CONFIG = yaml.safe_load(settings)

API_ID = CONFIG["api_id"]
API_HASH = CONFIG["api_hash"]
APP_SHORT_NAME = CONFIG["app_short_name"]
MESSAGES_CONFIG = CONFIG["messages"]
RAID_CONFIG = CONFIG["raid"]
CLIENT = None


def log(message):
    now = datetime.now()
    print("[" + now.strftime("%H:%M:%S.%f")[:-3] + "] " + message)


def random_thank_you():
    thank_yous = [
        "Thank you",
        "Thanks",
        "Tak",
        "Dank u",
        "Kiitos",
        "Merci",
        "Merci beaucoup",
        "Danke",
        "Danke schön",
        "Danke vielmals",
        "Mahalo",
        "Grazie",
        "Arigato",
        "Obrigado",
        "Gracias",
        "Xie xie",
        "Shukran",
        "Hvala",
        "Efharisto",
        "Dhanyavaad",
        "Spasiba",
        "Salamat",
        "Khob khun",
    ]
    return thank_yous[random.randrange(len(thank_yous))]


@functools.lru_cache()
def recommended_splay():
    # all of this assumes TG rate limit is 20 API calls per 1 minute
    segment_time = 72  # 120% of 60 seconds
    max_channels_per_segment = 20  # max calls per segment
    channels = len(RAID_CONFIG.keys())
    segments = math.ceil(channels / max_channels_per_segment)
    total_segment_time = segments * segment_time
    default_splay = math.ceil(segment_time / max_channels_per_segment)
    calculated_splay = math.ceil(total_segment_time / channels)
    return default_splay if calculated_splay > default_splay else calculated_splay


@functools.lru_cache()
def splay_map():
    count = 1
    result = {}
    for channel in RAID_CONFIG.keys():
        result[channel] = count * recommended_splay()
        count += 1
    return result


@functools.lru_cache()
def splay(channel):
    channel_splay = splay_map()
    return channel_splay[channel]


@asyncstdlib.lru_cache()
async def get_entity(channel):
    return await CLIENT.get_entity(channel)


def channel_map(channel):
    return {
        "name": channel,
        "splay": splay(channel),
        "wait_interval": RAID_CONFIG[channel].get("wait_interval", None),
        "message": MESSAGES_CONFIG[RAID_CONFIG[channel]["message_type"]],
    }


async def send_message(channel):
    log(f"Sending message to {channel}")
    try:
        message = MESSAGES_CONFIG[RAID_CONFIG[channel]["message_type"]]
        new_message = message + "\n" + random_thank_you() + "!"
        entity = await get_entity(channel)
        await CLIENT.send_message(entity, new_message)
    except FloodWaitError as fwe:
        log(f"FloodWaitError invoked; Forced waiting for {fwe}")
        await asyncio.sleep(delay=fwe.seconds)
    except SlowModeWaitError as swe:
        log(f"SlowModeWaitError invoked; Forced waiting for {swe}")
        await asyncio.sleep(delay=swe.seconds)


async def send_single_message(channel):
    log(f"Raiding {channel} once")
    await send_message(channel)


async def send_looped_message(channel):
    wait_interval = RAID_CONFIG[channel]["wait_interval"] + splay(channel)
    log(f"Raiding {channel} every {wait_interval} seconds")
    while True:
        await send_message(channel)
        await asyncio.sleep(wait_interval)


def message_once(channel):
    return "wait_interval" not in RAID_CONFIG[channel]


async def raid(channel):
    await asyncio.sleep(splay(channel))

    if message_once(channel):
        await send_single_message(channel)
    else:
        await send_looped_message(channel)


async def connect(channel):
    channels = []
    try:
        await asyncio.sleep(channel["splay"])
        log(f"Connecting to {channel['name']}")
        await CLIENT(functions.channels.JoinChannelRequest(channel=channel["name"]))
        channels.append(channel)
    except Exception as e:
        message = f"An exception was raised when connecting to {channel['name']}"
        if hasattr(e, "message"):
            message = message + "\n{e.message}"
        log(message)
    return channels


async def do_raid():
    tasks = [raid(channel) for channel in RAID_CONFIG.keys()]
    await asyncio.gather(*tasks)


async def do_connect():
    tasks = [connect(channel_map(channel)) for channel in RAID_CONFIG.keys()]
    await asyncio.gather(*tasks)


async def close():
    await CLIENT.log_out()


async def start():
    await CLIENT.start()
    await asyncio.sleep(10)

    log(f"Calculated splay: {recommended_splay()} seconds")
    log(
        "Splay will be added to connection and user defined wait intervals"
        + " to avoid Telegram rate limiting"
    )
    await do_connect()
    await do_raid()


if __name__ == "__main__":
    CLIENT = TelegramClient(APP_SHORT_NAME, API_ID, API_HASH)
    LOOP = asyncio.get_event_loop()
    try:
        LOOP.run_until_complete(start())
        LOOP.run_until_complete(close())
    except KeyboardInterrupt:
        LOOP.run_until_complete(close())
        sys.exit(0)

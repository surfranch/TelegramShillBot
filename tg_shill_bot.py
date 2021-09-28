import asyncio
import math
import random
import sys
from datetime import datetime

import asyncstdlib
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import FloodWaitError

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
        "Tak",
        "Dank u",
        "Kiitos",
        "Merci",
        "Danke",
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


def splay_map():
    count = 1
    result = {}
    for channel in RAID_CONFIG.keys():
        result[channel] = count * recommended_splay()
        count += 1
    return result


@asyncstdlib.lru_cache()
async def get_entity(channel):
    return await CLIENT.get_entity(channel)


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


async def raid(channel, splay):
    if "wait_interval" not in RAID_CONFIG[channel]:
        log(f"Raiding {channel} once")
        await asyncio.sleep(splay)
        await send_message(channel)
    else:
        wait_interval = RAID_CONFIG[channel]["wait_interval"] + splay
        log(f"Raiding {channel} every {wait_interval} seconds")
        await asyncio.sleep(splay)
        while True:
            await send_message(channel)
            await asyncio.sleep(wait_interval)


async def connect(channel, splay):
    try:
        await asyncio.sleep(splay)
        log(f"Connecting to {channel}")
        await CLIENT(functions.channels.JoinChannelRequest(channel=channel))
    except FloodWaitError as fwe:
        print(f"Waiting for {fwe}")
        await asyncio.sleep(delay=fwe.seconds)


async def do_raid():
    channel_splay = splay_map()
    tasks = [raid(channel, channel_splay[channel]) for channel in RAID_CONFIG.keys()]
    await asyncio.gather(*tasks)


async def do_connect():
    channel_splay = splay_map()
    tasks = [connect(channel, channel_splay[channel]) for channel in RAID_CONFIG.keys()]
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

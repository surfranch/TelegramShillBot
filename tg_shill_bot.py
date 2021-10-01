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
        "increase_wait_interval": RAID_CONFIG[channel].get(
            "increase_wait_interval", None
        ),
        "message": MESSAGES_CONFIG[RAID_CONFIG[channel]["message_type"]],
        "count": 0,
    }


def increment_count(channel):
    channel["count"] += 1
    return channel


async def handle_floodwaiterror(error, channel):
    log(
        "FloodWaitError invoked while sending a message;"
        + f" Forcing {error.seconds} second wait interval for {channel['name']}"
    )
    await asyncio.sleep(error.seconds)


def handle_slowmodewaiterror(error, channel):
    log(
        "SlowModeWaitError invoked while sending a message;"
        + f" Dynamically updating {channel['name']}'s calculated wait interval"
    )
    channel["calculated_wait_interval"] = error.seconds + 10
    return channel


def handle_unknownerror(error, channel):
    message = (
        "Unknown error invoked while sending a message; "
        + f" Abandoning sending messages to {channel['name']}"
    )
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log(message)
    channel["loop"] = False
    return channel


async def send_message(channel):
    channel = increment_count(channel)
    log(f"Sending message to {channel['name']} (#{channel['count']})")
    try:
        new_message = channel["message"] + "\n" + random_thank_you() + "!"
        entity = await get_entity(channel["name"])
        await CLIENT.send_message(entity, new_message)
    except FloodWaitError as fwe:
        await handle_floodwaiterror(fwe, channel)
    except SlowModeWaitError as smwe:
        channel = handle_slowmodewaiterror(smwe, channel)
    except Exception as e:
        channel = handle_unknownerror(e, channel)
    return channel


async def send_single_message(channel):
    log(f"Raiding {channel['name']} once")
    await send_message(channel)


def calculate_wait_interval(channel):
    calculated_wait_interval = channel["wait_interval"] + channel["splay"]
    channel["calculated_wait_interval"] = calculated_wait_interval
    return channel


def recalculate_wait_interval(channel):
    if channel["increase_wait_interval"]:
        channel["calculated_wait_interval"] += channel["increase_wait_interval"]
        log(
            f">> Recalculated {channel['name']} wait interval to"
            + f" {channel['calculated_wait_interval']} seconds"
        )
    return channel


async def send_looped_message(channel):
    channel = calculate_wait_interval(channel)
    channel["loop"] = True
    log(
        f"Raiding {channel['name']} every {channel['calculated_wait_interval']} seconds"
    )
    while channel["loop"]:
        channel = await send_message(channel)
        channel = recalculate_wait_interval(channel)
        await asyncio.sleep(channel["calculated_wait_interval"])


def message_once(channel):
    return not bool(channel["wait_interval"])


async def raid(channel):
    await asyncio.sleep(channel["splay"])

    if message_once(channel):
        await send_single_message(channel)
    else:
        await send_looped_message(channel)


def handle_connectionerror(error, channel):
    message = (
        "Unknown error invoked while connecting to a channel;"
        + f" Abandoning sending messages to {channel['name']}"
    )
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log(message)


async def connect(channel):
    is_connected = False
    try:
        await asyncio.sleep(channel["splay"])
        log(f"Connecting to {channel['name']}")
        await CLIENT(functions.channels.JoinChannelRequest(channel=channel["name"]))
        is_connected = True
    except Exception as e:
        handle_connectionerror(e, channel)
    channel["is_connected"] = is_connected
    return channel


async def do_raid(channels):
    tasks = [raid(channel) for channel in channels]
    await asyncio.gather(*tasks)


async def do_connect():
    tasks = [connect(channel_map(channel)) for channel in RAID_CONFIG.keys()]
    channels = await asyncio.gather(*tasks)
    connected_channels = filter(lambda channel: channel["is_connected"], channels)
    return connected_channels


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
    channels = await do_connect()
    await do_raid(channels)


if __name__ == "__main__":
    CLIENT = TelegramClient(APP_SHORT_NAME, API_ID, API_HASH)
    LOOP = asyncio.get_event_loop()
    try:
        LOOP.run_until_complete(start())
        LOOP.run_until_complete(close())
    except KeyboardInterrupt:
        LOOP.run_until_complete(close())
        sys.exit(0)

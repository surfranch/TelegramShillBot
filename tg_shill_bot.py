import asyncio
import random
import sys
import time
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
    ]
    return thank_yous[random.randrange(len(thank_yous))]


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


async def raid(channel):
    if "wait_interval" not in RAID_CONFIG[channel]:
        log(f"Raiding {channel} once")
        await send_message(channel)
    else:
        log(f"Raiding {channel} every {RAID_CONFIG[channel]['wait_interval']} seconds")
        while True:
            await send_message(channel)
            await asyncio.sleep(RAID_CONFIG[channel]["wait_interval"])


async def connect(channel):
    log(f"Connecting to {channel}")
    try:
        await CLIENT(functions.channels.JoinChannelRequest(channel=channel))
    except FloodWaitError as fwe:
        print(f"Waiting for {fwe}")
        await asyncio.sleep(delay=fwe.seconds)


def do_connect():
    loop = asyncio.get_event_loop()
    tasks = []
    for channel in RAID_CONFIG.keys():
        tasks.append(loop.create_task(connect(channel)))
    loop.run_until_complete(asyncio.wait(tasks))


def do_raid():
    loop = asyncio.get_event_loop()
    tasks = []
    for channel in RAID_CONFIG.keys():
        tasks.append(loop.create_task(raid(channel)))
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == "__main__":
    CLIENT = TelegramClient(APP_SHORT_NAME, API_ID, API_HASH)
    CLIENT.start()
    time.sleep(10)

    try:
        do_connect()
        do_raid()
    except KeyboardInterrupt:
        sys.exit(0)

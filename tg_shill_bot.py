import random
import sys
import time
import asyncio

from datetime import datetime
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


async def send_message(channel):
    log(f"Sending message to {channel}")
    try:
        message = MESSAGES_CONFIG[RAID_CONFIG[channel]["message_type"]]
        entity = await CLIENT.get_entity(channel)
        await CLIENT.send_message(entity, message)
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

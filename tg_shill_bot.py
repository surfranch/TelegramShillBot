# stdlib
import asyncio
import functools
import math
import random
import sys
import traceback
from datetime import datetime
from enum import Enum
from pathlib import Path

# custom
import asyncstdlib
import jsonschema
import yaml
from telethon import TelegramClient, functions
from telethon.errors.rpcerrorlist import (
    ChatWriteForbiddenError,
    FloodWaitError,
    SlowModeWaitError,
    MediaCaptionTooLongError,
)

VERSION = "v0.18"


class Style(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    RESET = "\033[0m"


def log_color(color, message):
    now = datetime.now()
    message = (
        color
        + "["
        + now.strftime("%H:%M:%S.%f")[:-3]
        + "] "
        + message
        + Style.RESET.value
    )
    print(message)
    return message


def log_green(message):
    return log_color(Style.GREEN.value, message)


def log_yellow(message):
    return log_color(Style.YELLOW.value, message)


def log_red(message):
    return log_color(Style.RED.value, message)


def thank_yous():
    return [
        "Cheers",
        "Thank you",
        "Thank you so much",
        "Thanks",
        "Thanks a bunch",
        "Thanks a million",
        "Ta",
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


def random_thank_you():
    return thank_yous()[random.randrange(len(thank_yous()))]


def header():
    surfranch = f"""{Style.CYAN.value}
┏━━━┓━━━━━━━━┏━┓┏━━━┓━━━━━━━━━━━━━┏┓━━
┃┏━┓┃━━━━━━━━┃┏┛┃┏━┓┃━━━━━━━━━━━━━┃┃━━
┃┗━━┓┏┓┏┓┏━┓┏┛┗┓┃┗━┛┃┏━━┓━┏━┓━┏━━┓┃┗━┓
┗━━┓┃┃┃┃┃┃┏┛┗┓┏┛┃┏┓┏┛┗━┓┃━┃┏┓┓┃┏━┛┃┏┓┃
┃┗━┛┃┃┗┛┃┃┃━━┃┃━┃┃┃┗┓┃┗┛┗┓┃┃┃┃┃┗━┓┃┃┃┃
┗━━━┛┗━━┛┗┛━━┗┛━┗┛┗━┛┗━━━┛┗┛┗┛┗━━┛┗┛┗┛
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
━━ {VERSION} ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Visit: https://t.me/joinchat/Sp3ACd_CTKA0MWIx{Style.RESET.value}
"""
    print(surfranch)
    return surfranch


def channels_to_raid():
    settings = load_settings()
    return settings["raid"].keys()


@functools.lru_cache()
def recommended_splay():
    # all of this assumes TG rate limit is 20 API calls per 1 minute
    segment_time = 72  # 120% of 60 seconds
    max_channels_per_segment = 20  # max calls per segment
    channels = len(channels_to_raid())
    segments = math.ceil(channels / max_channels_per_segment)
    total_segment_time = segments * segment_time
    default_splay = math.ceil(segment_time / max_channels_per_segment)
    calculated_splay = math.ceil(total_segment_time / channels)
    return default_splay if calculated_splay > default_splay else calculated_splay


@functools.lru_cache()
def splay_map():
    count = 1
    result = {}
    for channel in channels_to_raid():
        result[channel] = count * recommended_splay()
        count += 1
    return result


@functools.lru_cache()
def splay(channel):
    channel_splay = splay_map()
    return channel_splay[channel]


@asyncstdlib.lru_cache()
async def get_entity(channel):
    return await CLIENT.get_input_entity(channel)


def channel_to_raid(channel):
    settings = load_settings()
    return settings["raid"][channel]


def channel_message(channel):
    settings = load_settings()
    messages = settings["messages"]
    message_type = channel_to_raid(channel)["message_type"]
    if isinstance(message_type, str):
        message_type = [message_type]
    return list(map(lambda mt: messages[mt], message_type))


def channel_wait_interval(channel):
    return channel_to_raid(channel).get("wait_interval", None)


def channel_increase_wait_interval(channel):
    return channel_to_raid(channel).get("increase_wait_interval", None)


def channel_image(channel):
    return channel_to_raid(channel).get("image", None)


def channel_total_messages(channel):
    return channel_to_raid(channel).get("total_messages", 999999999999)


def channel_map(channel):
    return {
        "name": channel,
        "splay": splay(channel),
        "wait_interval": channel_wait_interval(channel),
        "increase_wait_interval": channel_increase_wait_interval(channel),
        "message": channel_message(channel),
        "last_message": -1,
        "image": channel_image(channel),
        "total_messages": channel_total_messages(channel),
        "count": 0,
        "is_connected": False,
    }


def increment_count(channel):
    channel["count"] += 1
    return channel


async def handle_message_floodwaiterror(error, channel):
    log_red(
        f"FloodWaitError invoked while sending a message to {channel['name']};"
        + f" Forcing a {error.seconds} second wait interval for all channels"
    )
    open_floodwaiterror()
    await asyncio.sleep(error.seconds)
    close_floodwaiterror()


def handle_slowmodewaiterror(error, channel):
    log_red(
        f"SlowModeWaitError invoked while sending a message to {channel['name']};"
        + f" Dynamically updating the channel's calculated wait interval to {error.seconds + 10}"
    )
    channel["calculated_wait_interval"] = error.seconds + 10
    return channel


def handle_mediacaptiontoolongerror(channel):
    log_red(
        f"MediaCaptionTooLongError invoked while sending a message to {channel['name']};"
        + " Abandoning sending all future messages"
    )
    channel["loop"] = False
    return channel


async def handle_chatwriteforbiddenerror(channel):
    one_hour = 60 * 60
    log_red(
        f"ChatWriteForbiddenError invoked while sending a message to {channel['name']};"
        + f" Forcing a {one_hour} second wait interval for this channel"
    )
    await asyncio.sleep(one_hour)


def handle_unknownerror(error):
    message = "Unknown error invoked while running bot; Abandoning all execution"
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log_red(message)
    traceback.print_exc()


def handle_unknownmessagingerror(error, channel):
    message = (
        f"Unknown error invoked while sending a message to {channel['name']};"
        + " Abandoning sending all future messages"
    )
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log_red(message)
    traceback.print_exc()
    channel["loop"] = False
    return channel


def open_floodwaiterror():
    STATE.update({"floodwaiterror_exists": True})


def close_floodwaiterror():
    STATE.update({"floodwaiterror_exists": False})


def floodwaiterror_exists():
    return STATE.get("floodwaiterror_exists", False)


def image_exists(channel):
    result = False
    if channel["image"]:
        path = Path(channel["image"])
        if path.is_file():
            result = True
        else:
            log_yellow(
                f">> Unable to locate {channel['name']}'s configured image {channel['image']};"
                + " Sending message without image"
            )
    return result


def randomize_message(channel, ty1=None, ty2=None):
    if not ty1:
        ty1 = random_thank_you()
    if not ty2:
        ty2 = random_thank_you()
    return channel["message"][channel["last_message"]] + "\n" + ty1 + " & " + ty2 + "!"


def next_message(channel):
    proposed_message = channel["last_message"] + 1
    possible_messages = len(channel["message"]) - 1
    if proposed_message > possible_messages:
        use_message = 0
    else:
        use_message = proposed_message
    channel["last_message"] = use_message
    return [randomize_message(channel), channel]


async def dispatch_message(message, channel):
    entity = await get_entity(channel["name"])
    channel = increment_count(channel)
    log_green(f"Sending message to {channel['name']} (#{channel['count']})")
    if image_exists(channel):
        await CLIENT.send_message(entity, message, file=channel["image"])
    else:
        await CLIENT.send_message(entity, message)
    return channel


async def send_message(channel):
    try:
        channel = await dispatch_message(*next_message(channel))
    except FloodWaitError as fwe:
        await handle_message_floodwaiterror(fwe, channel)
    except ChatWriteForbiddenError:
        await handle_chatwriteforbiddenerror(channel)
    except SlowModeWaitError as smwe:
        channel = handle_slowmodewaiterror(smwe, channel)
    except MediaCaptionTooLongError:
        channel = handle_mediacaptiontoolongerror(channel)
    except Exception as e:
        channel = handle_unknownmessagingerror(e, channel)
    return channel


async def send_single_message(channel):
    log_green(f"Raiding {channel['name']} once")
    await send_message(channel)


def calculate_wait_interval(channel):
    calculated_wait_interval = channel["wait_interval"] + channel["splay"]
    channel["calculated_wait_interval"] = calculated_wait_interval
    return channel


def recalculate_wait_interval(channel):
    if channel["loop"] and channel["increase_wait_interval"]:
        channel["calculated_wait_interval"] += channel["increase_wait_interval"]
        log_yellow(
            f">> Recalculated {channel['name']} wait interval to"
            + f" {channel['calculated_wait_interval']} seconds"
        )
    return channel


def resolve_total_messages(channel):
    if channel["count"] >= channel["total_messages"]:
        channel["loop"] = False
        channel["calculated_wait_interval"] = 1
        log_yellow(">> Allowed total messages reached; Stopping message loop")
    return channel


async def message_loop(channel):
    while channel["loop"]:
        if floodwaiterror_exists():
            log_yellow(
                f">> Skipped sending message to {channel['name']} due to active FloodWaitError"
            )
        else:
            channel = await send_message(channel)
            channel = recalculate_wait_interval(channel)
            channel = resolve_total_messages(channel)
        await asyncio.sleep(channel["calculated_wait_interval"])


async def send_looped_message(channel):
    channel = calculate_wait_interval(channel)
    channel["loop"] = True
    log_green(
        f"Raiding {channel['name']} every {channel['calculated_wait_interval']} seconds"
    )
    await message_loop(channel)


def message_once(channel):
    return not bool(channel["wait_interval"])


async def raid(channel):
    await asyncio.sleep(channel["splay"])

    if message_once(channel):
        await send_single_message(channel)
    else:
        await send_looped_message(channel)


async def handle_connection_floodwaiterror(error, channel):
    log_red(
        f"FloodWaitError invoked while connecting to {channel['name']};"
        + f" Forcing a {error.seconds} second wait interval for all channels"
    )
    open_floodwaiterror()
    await asyncio.sleep(error.seconds)
    close_floodwaiterror()


def handle_connectionerror(error, channel):
    message = (
        "Unknown error invoked while connecting to a channel;"
        + f" Abandoning sending messages to {channel['name']}"
    )
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log_red(message)


async def sleep_while_floodwaiterror_exists(channel):
    while floodwaiterror_exists():
        log_yellow(
            f">> Delaying connecting to {channel['name']} due to active FloodWaitError"
        )
        await asyncio.sleep(channel["splay"])


async def dispatch_connection(channel):
    await asyncio.sleep(channel["splay"])
    await sleep_while_floodwaiterror_exists(channel)
    log_green(f"Connecting to {channel['name']}")
    await CLIENT(functions.channels.JoinChannelRequest(channel=channel["name"]))
    channel["is_connected"] = True
    return channel


async def connect(channel):
    try:
        channel = await dispatch_connection(channel)
    except FloodWaitError as fwe:
        await handle_connection_floodwaiterror(fwe, channel)
    except Exception as e:
        handle_connectionerror(e, channel)
    return channel


async def do_raid(channels):
    tasks = [raid(channel) for channel in channels]
    await asyncio.gather(*tasks)


async def do_connect():
    tasks = [connect(channel_map(channel)) for channel in channels_to_raid()]
    channels = await asyncio.gather(*tasks)
    connected_channels = filter(lambda channel: channel["is_connected"], channels)
    return connected_channels


async def stop():
    try:
        await CLIENT.log_out()
    except Exception:
        pass


async def start():
    await CLIENT.start(phone_number())
    await asyncio.sleep(10)

    print("")
    log_green(f"Calculated splay: {recommended_splay()} seconds")
    log_green(
        "Splay will be added to connection and user defined wait intervals"
        + " to avoid Telegram rate limiting"
    )
    channels = await do_connect()
    await do_raid(channels)


def validate_account_settings(settings):
    schema = {
        "type": "object",
        "properties": {
            "api_id": {"type": "number"},
            "api_hash": {"type": "string"},
            "app_short_name": {"type": "string"},
            "phone_number": {"type": "string"},
            "messages": {"type": "object"},
            "raid": {"type": "object"},
        },
        "additionalProperties": False,
        "required": [
            "api_id",
            "api_hash",
            "app_short_name",
            "phone_number",
            "messages",
            "raid",
        ],
    }
    jsonschema.validate(settings, schema)


def validate_messages_settings(settings):
    schema = {
        "type": "object",
        "patternProperties": {"^[a-zA-Z0-9_]+$": {"type": "string"}},
        "additionalProperties": False,
        "minProperties": 1,
    }
    jsonschema.validate(settings, schema)


def validate_raid_settings(settings):
    schema = {
        "type": "object",
        "patternProperties": {
            "^.+$": {
                "type": "object",
                "properties": {
                    "message_type": {
                        "anyOf": [
                            {
                                "type": "string",
                                "pattern": "^[a-zA-Z0-9_]+$",
                            },
                            {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                    "type": "string",
                                    "pattern": "^[a-zA-Z0-9_]+$",
                                },
                            },
                        ]
                    },
                    "wait_interval": {"type": "number", "exclusiveMinimum": 0},
                    "increase_wait_interval": {"type": "number", "exclusiveMinimum": 0},
                    "total_messages": {"type": "number", "exclusiveMinimum": 0},
                    "image": {"type": "string"},
                },
                "additionalProperties": False,
                "required": [
                    "message_type",
                ],
            }
        },
        "additionalProperties": False,
        "minProperties": 1,
    }
    jsonschema.validate(settings, schema)


@functools.lru_cache()
def load_settings(path="settings.yml"):
    with open(path, "r", encoding="utf8") as settings_file:
        try:
            settings = yaml.safe_load(settings_file)
        except Exception as e:
            print(
                f"""
{Style.RED.value}
!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#
!@#                                                !@#
!@#   THE `settings.yml` FILE IS NOT VALID YAML    !@#
!@#                                                !@#
!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#!@#
{Style.RESET.value}{Style.YELLOW.value}

BEFORE ASKING QUESTIONS IN THE SURFRANCH CHANNEL, PLEASE GIVE A BEST EFFORT
TO FIX THE YAML ERRORS YOURSELF USING THIS LINTER

>>>   http://www.yamllint.com/   <<<

IF YOU KNOW NOTHING ABOUT THE YAML SYNTAX, WE RECOMMEND READING THIS TUTORIAL

>>>   https://gettaurus.org/docs/YAMLTutorial/   <<<"""
            )
            raise e

        validate_account_settings(settings)
        validate_messages_settings(settings["messages"])
        validate_raid_settings(settings["raid"])
    return settings


def handle_start_floodwaiterror(error):
    message = (
        "FloodWaitError invoked while communicating with Telegram during start;"
        + " Nothing can be done at this time; Abandoning all execution"
    )
    if hasattr(error, "message"):
        message = message + f"\n{error.message}"
    log_red(message)
    traceback.print_exc()


def api_id():
    settings = load_settings()
    return settings["api_id"]


def api_hash():
    settings = load_settings()
    return settings["api_hash"]


def app_short_name():
    settings = load_settings()
    return settings["app_short_name"]


def phone_number():
    settings = load_settings()
    return settings["phone_number"]


if __name__ == "__main__":
    header()
    CLIENT = TelegramClient(app_short_name(), api_id(), api_hash())
    STATE = {}
    LOOP = asyncio.get_event_loop()
    try:
        LOOP.run_until_complete(start())
        LOOP.run_until_complete(stop())
    except KeyboardInterrupt:
        LOOP.run_until_complete(stop())
        sys.exit(0)
    except FloodWaitError as start_fwe:
        handle_start_floodwaiterror(start_fwe)
        LOOP.run_until_complete(stop())
    except Exception as start_error:
        handle_unknownerror(start_error)
        LOOP.run_until_complete(stop())

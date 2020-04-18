# -*- coding: utf-8 -*-

import asyncio
import datetime
import logging
from typing import Any, Callable, Dict, Union, MutableMapping, Mapping

import colorama
import fortnitepy
import toml
from colorama import deinit, init
from colorama import Fore as Color

from http_client import HttpClient

init()

log = logging.getLogger(__name__)


def time() -> str:
    return datetime.datetime.now().strftime("%Y-%b-%d | %I:%M %p")


def date_print(*args, **kwargs):
    print(f"[{time()}]", *args, **kwargs)


def colored_print(text: str,
                  color: Color,
                  *args,
                  **kwargs) -> None:

    print(f"{color}[{time()}]{text}", *args, **kwargs)
    print(colorama.Style.RESET_ALL, end="")
    print(colorama.Fore.RESET, end="")


class MainClient:
    def __init__(self, command_prefix):
        self.commands: Dict[str, Callable] = {}
        self._command_prefix = command_prefix
        self.client = None
        self._device_cache: Dict[Any, Any] = self.read_toml_file(
            "device_auth.toml"
        )
        log.debug(f"Loaded device_auth.toml| Content: [REDACTED]")
        self.device_id = self._device_cache["device_id"]
        self.email = self._device_cache["email"]
        self.secret = self._device_cache["secret"]
        self.client_id = self._device_cache["account_id"]
        self._settings: Dict[Any, Any] = self.read_toml_file(
            "settings.toml"
        )
        log.debug(f"Loaded settings.toml| Content: {self._settings}")
        if self._settings["account"]["debug"]:
            log.setLevel(logging.DEBUG)
            h = logging.StreamHandler()
            h.setLevel(logging.DEBUG)
            log.addHandler(h)
        self._account_settings: Dict[Any, Any] = self._settings["account"]
        self.owner_mode = self._account_settings["owner_mode"]
        self.owners = set(self._account_settings["owners"] if self.owner_mode == True else [])

    @staticmethod
    def read_toml_file(file_location: str) -> MutableMapping[str, Any]:
        with open(file_location, "r+") as fd:
            return toml.load(fd)

    @staticmethod
    def dump_dictionary_to_toml_file(o: Mapping[str, Any],
                                     file_location: str) -> None:
        with open(file_location, "w") as fd:
            toml.dump(o, fd)

    @property
    def command_prefix(self):
        return self._command_prefix

    def register_command(self, command_name: str, function: Callable) -> None:
        log.debug(f"registered {self.command_prefix}{command_name} as a"
                  "command")
        if not asyncio.iscoroutinefunction(function):
            raise TypeError("Function must be a coroutine.")
        self.commands[f"{self.command_prefix}{command_name}"] = function

    def get_permission(self, message: fortnitepy.FriendMessage) -> bool:
        if self.owner_mode:
            if not message.author.display_name in self.owners:
                if not message.author.id in self.owners:
                    return False
        return True

    async def process_command(self, command, message) -> None:
        log.debug(f"Processing {command.__name__} as a command")
        permission = self.get_permission(message)
        if not permission:
            log.debug(f"{message.author.display_name} doesn't have permission to run this command, skipping")
            return
        return await command(message)

    async def test_commands(self, message: fortnitepy.FriendMessage) -> None:
        log.debug(f"Received message: {message.content}")
        command, *_ = message.content.split(" ")
        if not command.startswith("!"):
            return
        if command in self.commands.keys():
            await self.process_command(self.commands[command], message)

    def command(self,
                coro: Callable
                ) -> Callable[[fortnitepy.FriendMessage], Any]:
        self.register_command(coro.__name__, coro)

        def inner(*args, **kwargs):
            return coro(*args, **kwargs)
        return inner

    @staticmethod
    def get_code():
        return input("Exchange code? ")

    async def on_ready(self):
        print(f"ready as {self.client.user.display_name}")

    def start(self):
        self.client = fortnitepy.Client(
            auth=fortnitepy.AdvancedAuth(
                email=self.email,
                exchange_code=self.get_code,
                device_id=self.device_id,
                account_id=self.client_id,
                secret=self.secret
            )
        )
        self.client.add_event_handler("friend_message", self.test_commands)
        self.client.add_event_handler("ready", self.on_ready)
        self.client.add_event_handler("party_invite", on_invite)

    def bind_to_http_client(self):
        self.http = HttpClient(self.client)


bot = MainClient(command_prefix="!")


@bot.command
async def playlist(message):
    await bot.client.user.party.set_playlist(message.content)


@bot.command
async def set_ready(message, lol):
    await bot.client.user.party.me.set_ready(
        fortnitepy.ReadyState.SITTING_OUT
    )

@bot.command
async def skin(message):
    await bot.http.fin

@bot.command
async def test(message):
    from pprint import pprint
    pprint(dir(message))


async def on_invite(invite):
    if invite.sender.display_name == "caIculator":
        await invite.accept()

def unload_colorama():
    deinit()


colored_print(r"""
__
| |__   ___   __ _| |_
| '_ \ / _ \ / _` | __|
| |_) | (_) | (_| | |_
|_.__/ \___/ \__,_|\__|
 _   ___
/ | / _ \
| || | | |
| || |_| |
|_(_\___/
""", Color.CYAN)
bot.start()
bot.client.run()

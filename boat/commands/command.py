from typing import Callable
from inspect import signature, Signature
from enum import Enum
from .exceptions import InvalidParameters
from .context import MessageContext

class Mode(Enum):
    POSITIONAL = 0
    NON_POSITIONAL = 1

class Parameter(Enum):
    CONTEXT = 0
    POSITIONAL = 1
    NON_POSITIONAL = 2

class Command:
    def __init__(self, fn: Callable, prefix: str):
        self.signature = signature(fn)
        self.function = fn
        self.uses_non_positional = False
        self.parse_params()
        self.prefix = prefix

    def parse_params(self):
        args = str(self.signature)[1:-1:].replace(" ", "").split(",")
        mode = Mode.POSITIONAL
        self.length = len(args)
        if args == ['']:
            raise InvalidParameters()
        args[0] = Parameter.CONTEXT
        for index, arg in enumerate(args[1:], 1):
            if arg == "*":
                mode = Mode.NON_POSITIONAL
                self.length -= 1
                continue
            if mode == Mode.POSITIONAL:
                args[index] = Parameter.POSITIONAL
            if mode == Mode.NON_POSITIONAL:
                args[index] = Parameter.NON_POSITIONAL
            if mode == Mode.NON_POSITIONAL:
                break
        self.params = args

    async def __call__(self, message: MessageContext):
        message._content = message.content[len(
            self.prefix + self.function.__name__ + " "):
            ]  # Removes the invoker
        await self.function(message)

# In progress




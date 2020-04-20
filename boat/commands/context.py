import fortnitepy
from typing import Union
from enum import Enum


class MessageType(Enum):
    PARTY = 0
    FRIEND = 1


class MessageContext(fortnitepy.message.MessageBase):
    def __init__(self,
                 message: Union[fortnitepy.PartyMessage, fortnitepy.FriendMessage] # noqa
                 ):
        super().__init__(message.client, message.author, message.content)
        if isinstance(message, fortnitepy.FriendMessage):
            self.type = MessageType.FRIEND
        else:
            self.type = MessageType.PARTY

    async def reply(self, content: str) -> None:
        """|coro|

        Replies to the message with the given content.

        Parameters
        ----------
        content: :class:`str`
            The content of the message
        """
        if self.type == MessageType.FRIEND:
            return await self.author.send(content)
        await self.party.send(content)

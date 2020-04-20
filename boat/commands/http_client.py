import aiohttp
import fortnitepy
import toml
from typing import List, Set, Union, Optional
from enum import Enum


class CosmeticType(Enum):
    SKIN = "CID"
    EMOTE = "EID"
    BACKPACK = "BID"
    PICKAXE = "PID"
    EMOJI = "EMOJI"
    PET = "PET"
    CONTRAIL = "CONTRAIL"


class HttpClient:
    def __init__(self, client: fortnitepy.Client):
        with open("settings.toml") as s:  # Turn this into an arg later
            self._cache = toml.load(s)["account"]["preferences"]
            self.blocklist: List[str] = self._cache["blocklist"]
            self.owner_mode: bool = self._cache["owner_mode"]
            self.owners: Set[str] = set(self._cache["owners"])
        self.client = client
        self.usermember: fortnitepy.ClientPartyMember = self.client.user.party.me # noqa

    @staticmethod
    async def get_cosmetic_type(cosmetic_id: str) -> CosmeticType:
        cosmetic_id = cosmetic_id.upper()
        for cosmetic_type in CosmeticType:
            if cosmetic_id.startswith(cosmetic_id):
                return cosmetic_type
        return CosmeticType.SKIN

    async def get_session(self) -> None:
        self.session = aiohttp.ClientSession()

    async def set_cosmetic(
         self,
         cosmetic_id: str,
         operator: Union[fortnitepy.Friend, fortnitepy.PartyMember],
         variants,
         cosmetic_type: Optional[CosmeticType] = None,
         *args,
         **kwargs) -> bool:
        """
        Sets a cosmetic and returns True if it was sucessful else false
        """
        if not self.owner_mode:
            return await self._set_cosmetic(
                cosmetic_id,
                cosmetic_type if cosmetic_type is not None else self.get_cosmetic_type( # noqa
                    cosmetic_id
                    ),
                variants=variants,
                **kwargs)
        else:
            if operator in self.owners:
                return await self._set_cosmetic(
                    cosmetic_id,
                    cosmetic_type if cosmetic_type is not None else self.get_cosmetic_type( # noqa
                        cosmetic_id
                        ),
                    variants=variants,
                    **kwargs)
            else:
                return False
        return False

    async def _set_cosmetic(self,
                            cosmetic_id: str,
                            cosmetic_type: Union[CosmeticType, object],
                            variants: dict = {},
                            **kwargs) -> bool:
        try:
            if cosmetic_type == CosmeticType.SKIN:
                await self.usermember.set_outfit(cosmetic_id,
                                                 variants=variants,
                                                 **kwargs
                                                 )
            elif cosmetic_type == CosmeticType.EMOTE:
                await self.usermember.set_emote(cosmetic_id,
                                                variants=variants,
                                                **kwargs
                                                )
            elif cosmetic_type == CosmeticType.BACKPACK:
                await self.usermember.set_backpack(cosmetic_id,
                                                   variants=variants,
                                                   **kwargs
                                                   )
            elif cosmetic_type == CosmeticType.EMOJI:
                await self.usermember.set_emoji(cosmetic_id,
                                                variants=variants,
                                                **kwargs
                                                )
            elif cosmetic_type == CosmeticType.PET:
                await self.usermember.set_pet(cosmetic_id,
                                              variants=variants,
                                              **kwargs
                                              )  # Fix this mess later
            elif cosmetic_type == CosmeticType.PICKAXE:
                await self.usermember.set_pickaxe(
                    cosmetic_id, variants=variants, **kwargs
                )
            elif cosmetic_type == CosmeticType.PICKAXE:
                await self.usermember.set_pickaxe(
                    cosmetic_id, variants=variants, **kwargs
                )
            elif cosmetic_type == CosmeticType.CONTRAIL:
                await self.usermember.set_contrail(
                    cosmetic_id, variants=variants, **kwargs
                )
        except fortnitepy.FortniteException:
            raise
        return True

    #async def get_cosmetic_by_display_name()  # In progress

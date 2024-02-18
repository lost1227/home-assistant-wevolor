"""Add 'favorite' button entities for all the shades."""

from __future__ import annotations

from pywevolor import Wevolor

import logging

from homeassistant.components.button import ButtonEntity

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import  DOMAIN, CONFIG_UID, CONFIG_CHANNELS, CONFIG_CHANNEL_NAME, CONFIG_CHANNEL_FAVORITE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up buttons for each Wevolor shade."""

    wevolor = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        WevolorFavoriteButton(wevolor, config_entry.data[CONFIG_UID], channel)
            for channel in config_entry.data[CONFIG_CHANNELS].items()
            if not channel[1][CONFIG_CHANNEL_FAVORITE]
    ]

    async_add_entities(entities, True)


class WevolorFavoriteButton(ButtonEntity):
    """Button entity to set a wevolor blind to favorite position."""

    _attr_has_entity_name = True
    _attr_translation_key = "favorite_button"

    _channels: list[int]
    _wevolor: Wevolor

    def __init__(self, wevolor: Wevolor, uid: str, channel: tuple[str, dict[str, any]]):
        """Set up wevolor and channel properties."""
        channel_id = channel[0]
        channel_config = channel[1]

        self._attr_unique_id = f"{uid}-{channel_id}-fav"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{uid}-{channel_id}")},
            "name": f"Wevolor {channel_config[CONFIG_CHANNEL_NAME]}",
            "manufacturer": "Wevolor"
        }
        self._wevolor = wevolor
        self._channel = int(channel_id)
        self._attr_translation_placeholders = {
            "name": channel_config[CONFIG_CHANNEL_NAME]
        }
        self._attr_icon = "mdi:heart"

        _LOGGER.debug("Create WevolorFavoriteButton instance '%s'", self._attr_unique_id)

    async def async_press(self) -> None:
        """Set this channel to favorite position."""
        if self._wevolor:
            await self._wevolor.favorite_blind(self._channel)

"""Cover component for shades controlled by the Wevolor controller."""

from __future__ import annotations

from pywevolor import Wevolor

import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.components.cover import (
    CoverEntityFeature,
    CoverDeviceClass,
    CoverEntity,
)

from .const import CONFIG_CHANNELS, CONFIG_UID, DOMAIN, CONFIG_CHANNEL_NAME, CONFIG_CHANNEL_TILT, CONFIG_CHANNEL_FAVORITE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the Wevolor shades."""

    wevolor = hass.data[DOMAIN][config_entry.entry_id]
    channels = config_entry.data[CONFIG_CHANNELS].items()

    entities = [WevolorShade(wevolor, config_entry.data[CONFIG_UID], channel) for channel in channels]
    async_add_entities(entities, True)


class WevolorShade(CoverEntity):
    """Cover entity for control of Wevolor remote channel."""

    _attr_assumed_state = True
    _attr_has_entity_name = True
    _attr_name = None

    _channel: int
    _wevolor: Wevolor
    _down_is_favorite: bool

    def __init__(self, wevolor: Wevolor, uid: str, channel: tuple[str, dict[str, any]]):
        """Create this wevolor shade cover entity."""
        channel_id = channel[0]
        channel_config = channel[1]

        self._attr_unique_id = f"{uid}-{channel_id}-cov"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{uid}-{channel_id}")},
            "name": f"Wevolor {channel_config[CONFIG_CHANNEL_NAME]}",
            "manufacturer": "Wevolor"
        }
        self._wevolor = wevolor
        self._channel = int(channel_id)
        self._down_is_favorite = channel_config[CONFIG_CHANNEL_FAVORITE]
        self._attr_device_class = CoverDeviceClass.SHADE
        self._attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        if channel_config[CONFIG_CHANNEL_TILT]:
            self._attr_device_class = CoverDeviceClass.BLIND
            self._attr_supported_features |= (
                CoverEntityFeature.OPEN_TILT | CoverEntityFeature.CLOSE_TILT | CoverEntityFeature.STOP_TILT
            )

        _LOGGER.debug("Create WevolorShade instance '%s'", self._attr_unique_id)

    async def async_stop_cover(self, **kwargs):
        """Stop motion."""
        await self._wevolor.stop_blind(self._channel)

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self._wevolor.open_blind(self._channel)

    async def async_close_cover(self, **kwargs):
        """Close the cover."""
        if self._down_is_favorite:
            await self._wevolor.favorite_blind(self._channel)
        else:
            await self._wevolor.close_blind(self._channel)

    async def async_open_cover_tilt(self, **kwargs):
        """Open tilt."""
        await self._wevolor.open_blind_tilt(self._channel)

    async def async_close_cover_tilt(self, **kwargs):
        """Close tilt."""
        await self._wevolor.close_blind_tilt(self._channel)

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop tilt."""
        await self._wevolor.stop_blind_tilt(self._channel)

    @property
    def is_closed(self) -> bool | None:
        """Since Wevolor does not expose any status, return None here."""
        return None

"""The Wevolor Control for Levolor Motorized Blinds integration."""
from __future__ import annotations

from pywevolor import Wevolor

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONFIG_HOST, DOMAIN, CONFIG_UID, CONFIG_CHANNELS, CONFIG_CHANNEL_NAME, CONFIG_CHANNEL_TILT, CONFIG_CHANNEL_FAVORITE

from .config_flow import ConfigFlow

PLATFORMS: list[str] = [
    Platform.COVER,
    Platform.BUTTON
]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wevolor Control for Levolor Motorized Blinds from a config entry."""

    # hass.data is a global dictionary accessible everywhere in which we can store arbitrary data.
    # We store a Wevolor instance so that both the Cover and Button platforms can access the same
    # instance.
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = Wevolor(
        host=entry.data[CONFIG_HOST]
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s to %s", config_entry.version, ConfigFlow.VERSION)

    if config_entry.version > ConfigFlow.VERSION:
        _LOGGER.error(f"Rejecting attempt to downgrade configuration entry from %s to %s", config_entry.version, ConfigFlow.VERSION)
        return False

    if config_entry.version == 1:
        new_data = {
            CONFIG_HOST: config_entry.data["host"],
            CONFIG_UID: config_entry.data["uid"],
            CONFIG_CHANNELS: {}
        }

        for i in range(6):
            if config_entry.data[f"channel_{i+1}"]:
                new_data[CONFIG_CHANNELS][str(i+1)] = {
                    CONFIG_CHANNEL_NAME: f"Channel {i+1}",
                    CONFIG_CHANNEL_TILT: config_entry.data["support_tilt"],
                    CONFIG_CHANNEL_FAVORITE: False
                }
            config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new_data)

        _LOGGER.debug("Migration to version 2 successful")

        return True

    _LOGGER.error("Unknown config entry schema version %s", config_entry.version)

    return False

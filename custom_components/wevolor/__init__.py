"""The Wevolor Control for Levolor Motorized Blinds integration."""
from __future__ import annotations

from pywevolor import Wevolor

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONFIG_HOST, DOMAIN

PLATFORMS: list[str] = [
    Platform.COVER,
    Platform.BUTTON
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wevolor Control for Levolor Motorized Blinds from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = Wevolor(
        host=entry.data[CONFIG_HOST]
    )

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

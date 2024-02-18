"""Config flow for Wevolor Control for Levolor Motorized Blinds integration."""
from __future__ import annotations

import logging
from typing import Any

from pywevolor import Wevolor
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import selector

from .const import CONFIG_HOST, CONFIG_UID, DOMAIN, CONFIG_CHANNELS, CONFIG_CHANNEL_NAME, CONFIG_CHANNEL_TILT, CONFIG_CHANNEL_FAVORITE

_LOGGER = logging.getLogger(__name__)

CONFIG_BRIDGE_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_HOST): str,
        CONFIG_CHANNELS: selector({
            "select": {
                "translation_key": "channels",
                "options": [{"label": f"channel_{i+1}", "value": str(i+1)} for i in range(6)],
                "multiple": True
            }
        })
    }
)

CONFIG_CHANNEL_SCHEMA = vol.Schema(
    {
        vol.Required(CONFIG_CHANNEL_NAME): str,
        vol.Required(CONFIG_CHANNEL_TILT, default=False): bool,
        vol.Required(CONFIG_CHANNEL_FAVORITE, default=False): bool
    }
)


async def validate_config_bridge_input(data: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Validate the user input allows us to connect."""

    wevolor = Wevolor(data[CONFIG_HOST])
    status = await wevolor.get_status()

    if not status:
        raise CannotConnect

    if len(data[CONFIG_CHANNELS]) == 0:
        # TODO: Do this check with a validator
        raise ValueError('Must specify at least 1 channel')

    bridge_config = {
        CONFIG_HOST: data[CONFIG_HOST],
        CONFIG_UID: status["uid"],
        CONFIG_CHANNELS: data[CONFIG_CHANNELS]
    }

    title = status["remote"]
    if not title:
        title = "Wevolor-" + status["uid"]

    return (title, bridge_config)

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wevolor Control for Levolor Motorized Blinds."""

    VERSION = 2

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Config flow next step: 'config_bridge'")
        return self.async_show_form(
            step_id="config_bridge", data_schema=CONFIG_BRIDGE_SCHEMA
        )

    async def async_step_config_bridge(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors = {}
        try:
            title, bridge_config = await validate_config_bridge_input(user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except Exception as err:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception: %s", err)
            errors["base"] = "unknown"
        else:
            _LOGGER.debug("Data validated for step 'config_bridge'")
            self.title = title
            self.bridge_config = bridge_config
            self.channel_config = {}

            await self.async_set_unique_id(bridge_config[CONFIG_UID])
            self._abort_if_unique_id_configured(updates={CONFIG_HOST: bridge_config[CONFIG_HOST]})

            channel = self.next_channel()

            _LOGGER.debug("Config flow next_step: 'config_channel' for channel %s", channel)

            return self.async_show_form(step_id="config_channel",
                                        data_schema=CONFIG_CHANNEL_SCHEMA,
                                        description_placeholders={
                                            "channel": channel
                                        })

        return self.async_show_form(
            step_id="config_bridge", data_schema=CONFIG_CHANNEL_SCHEMA, errors=errors
        )

    def next_channel(self) -> str|None:
        for channel in self.bridge_config["channels"]:
            if channel not in self.channel_config:
                return channel
        return None

    async def async_step_config_channel(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        channel = self.next_channel()

        self.channel_config[channel] = {
            CONFIG_CHANNEL_NAME: user_input[CONFIG_CHANNEL_NAME],
            CONFIG_CHANNEL_TILT: user_input[CONFIG_CHANNEL_TILT],
            CONFIG_CHANNEL_FAVORITE: user_input[CONFIG_CHANNEL_FAVORITE]
        }

        next_channel = self.next_channel()

        if next_channel is not None:
            _LOGGER.debug("Config flow next_step: 'config_channel' for channel %s", next_channel)
            return self.async_show_form(step_id="config_channel",
                                        data_schema=CONFIG_CHANNEL_SCHEMA,
                                        description_placeholders={
                                            "channel": next_channel
                                        })

        data = {
            CONFIG_HOST: self.bridge_config[CONFIG_HOST],
            CONFIG_UID: self.bridge_config[CONFIG_UID],
            CONFIG_CHANNELS: self.channel_config
        }
        _LOGGER.debug("Config flow finished: create config entry '%s'", self.title)
        return self.async_create_entry(title=self.title, data=data)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

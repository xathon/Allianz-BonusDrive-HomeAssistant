"""Adds config flow for Bonusdrive."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import callback
from homeassistant.helpers import selector
from slugify import slugify

from .api import (
    BonusdriveApiClient,
    BonusdriveApiClientAuthenticationError,
    BonusdriveApiClientCommunicationError,
    BonusdriveApiClientError,
)
from .const import CONF_BASE_URL, CONF_PHOTON_URL, DEFAULT_BASE_URL, DOMAIN, LOGGER


class BonusdriveFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Bonusdrive."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BonusdriveOptionsFlowHandler:
        """Get the options flow for this handler."""
        return BonusdriveOptionsFlowHandler(config_entry)

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                await self._test_credentials(
                    base_url=user_input.get(CONF_BASE_URL, DEFAULT_BASE_URL),
                    email=user_input[CONF_EMAIL],
                    password=user_input[CONF_PASSWORD],
                )
            except BonusdriveApiClientAuthenticationError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except BonusdriveApiClientCommunicationError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except BonusdriveApiClientError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                # Ensure base_url is saved in data
                data = {**user_input}
                if CONF_BASE_URL not in data:
                    data[CONF_BASE_URL] = DEFAULT_BASE_URL

                await self.async_set_unique_id(
                    unique_id=slugify(user_input[CONF_EMAIL])
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL],
                    data=data,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_EMAIL,
                        default=(user_input or {}).get(CONF_EMAIL, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.EMAIL,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                    vol.Optional(
                        CONF_BASE_URL,
                        default=DEFAULT_BASE_URL,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                    vol.Optional(
                        CONF_PHOTON_URL,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, base_url: str, email: str, password: str) -> None:
        """Validate credentials."""
        client = BonusdriveApiClient(
            hass=self.hass,
            base_url=base_url,
            email=email,
            password=password,
        )
        await client.async_authenticate()


class BonusdriveOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Bonusdrive."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry data with new values
            new_data = {**self.config_entry.data, **user_input}
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=new_data,
            )
            # Reload the integration to apply changes
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PHOTON_URL,
                        default=self.config_entry.data.get(CONF_PHOTON_URL, ""),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.URL,
                        ),
                    ),
                },
            ),
        )

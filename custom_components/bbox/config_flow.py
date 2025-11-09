"""Config flow for Bbox integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

import voluptuous as vol
from aiobbox.client import BboxApi
from aiobbox.exceptions import (
    BboxApiError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxTimeoutError,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_PASSWORD
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import CONF_BASE_URL, DEFAULT_BASE_URL, DOMAIN

if TYPE_CHECKING:
    from collections.abc import Mapping

    from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    session = async_get_clientsession(hass)
    base_url = data[CONF_BASE_URL]

    # Ensure URL ends with /
    if not base_url.endswith("/"):
        base_url = base_url + "/"

    api = BboxApi(
        password=data[CONF_PASSWORD],
        base_url=base_url,
        session=session,
    )

    try:
        await api.authenticate()
        router = await api.get_router_info()
    finally:
        await api.close()

    # Return info that you want to store in the config entry.
    return {
        "title": router.modelname,
        "serial": router.serialnumber,
    }


class BboxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Bbox."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except BboxInvalidCredentialsError:
                errors["base"] = "invalid_auth"
            except BboxRateLimitError:
                errors["base"] = "rate_limit"
            except BboxTimeoutError:
                errors["base"] = "cannot_connect"
            except BboxApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID to prevent duplicate entries
                await self.async_set_unique_id(info["serial"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_BASE_URL, default=DEFAULT_BASE_URL): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_reauth(self, _: Mapping[str, Any]) -> ConfigFlowResult:
        """Handle re-authentication."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm re-authentication."""
        errors: dict[str, str] = {}

        if user_input is not None:
            entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
            assert entry is not None

            data = {
                CONF_BASE_URL: entry.data[CONF_BASE_URL],
                CONF_PASSWORD: user_input[CONF_PASSWORD],
            }

            try:
                await validate_input(self.hass, data)
            except BboxInvalidCredentialsError:
                errors["base"] = "invalid_auth"
            except BboxRateLimitError:
                errors["base"] = "rate_limit"
            except BboxTimeoutError:
                errors["base"] = "cannot_connect"
            except BboxApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data=data,
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema({vol.Required(CONF_PASSWORD): str}),
            errors=errors,
        )

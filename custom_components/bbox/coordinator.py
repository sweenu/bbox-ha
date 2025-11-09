"""Data update coordinator for Bbox integration."""

from __future__ import annotations

import logging

from aiobbox.client import BboxApi
from aiobbox.exceptions import (
    BboxApiError,
    BboxSessionExpiredError,
    BboxTimeoutError,
    BboxUnauthenticatedError,
)
from aiobbox.models import Host, Router
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_BASE_URL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BboxData:
    """Class to hold Bbox data."""

    def __init__(self, router: Router, hosts: list[Host]) -> None:
        """Initialize Bbox data."""
        self.router: Router = router
        self.hosts: list[Host] = hosts


class BboxDataUpdateCoordinator(DataUpdateCoordinator[BboxData]):
    """Class to manage fetching Bbox data from the router."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.config_entry = entry
        self._api: BboxApi | None = None
        self._base_url: str = entry.data[CONF_BASE_URL]
        self._password: str = entry.data[CONF_PASSWORD]

    @property
    def api(self) -> BboxApi:
        """Return the API client."""
        if self._api is None:
            session = async_get_clientsession(self.hass)
            self._api = BboxApi(
                password=self._password,
                base_url=self._base_url,
                session=session,
            )
        return self._api

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        try:
            await self.api.authenticate()
        except BboxTimeoutError as err:
            raise UpdateFailed(
                f"Timeout connecting to Bbox at {self._base_url}"
            ) from err
        except BboxApiError as err:
            raise UpdateFailed(f"Failed to connect to Bbox: {err}") from err

    async def _async_update_data(self) -> BboxData:
        """Fetch data from Bbox router."""
        try:
            # Fetch router info and connected hosts
            router = await self.api.get_router_info()
            hosts = await self.api.get_hosts()

            return BboxData(router=router, hosts=hosts)

        except (BboxSessionExpiredError, BboxUnauthenticatedError) as err:
            # Session expired, trigger re-authentication
            _LOGGER.debug("Session expired, triggering re-authentication")
            raise ConfigEntryAuthFailed(
                "Session expired, please re-authenticate"
            ) from err

        except BboxTimeoutError as err:
            raise UpdateFailed(f"Timeout fetching Bbox data: {err}") from err

        except BboxApiError as err:
            raise UpdateFailed(f"Error fetching Bbox data: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown the coordinator."""
        if self._api is not None:
            await self._api.close()
            self._api = None

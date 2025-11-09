"""Base entity for Bbox integration."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_BASE_URL, DOMAIN
from .coordinator import BboxDataUpdateCoordinator


class BboxEntity(CoordinatorEntity[BboxDataUpdateCoordinator]):
    """Base entity for Bbox integration."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BboxDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        # Set up device info for the router
        router = coordinator.data.router
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, router.serialnumber)},
            name=router.modelname,
            manufacturer="Bouygues Telecom",
            model=router.modelclass,
            serial_number=router.serialnumber,
            sw_version=router.running.version,
            configuration_url=coordinator.config_entry.data.get(CONF_BASE_URL),
        )

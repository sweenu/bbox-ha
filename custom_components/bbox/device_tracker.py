"""Device tracker platform for Bbox integration."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from aiobbox.models import Host
from homeassistant.components.device_tracker import ScannerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.core import callback
from homeassistant.helpers.device_registry import format_mac

from .const import (
    ATTR_CONNECTION_SPEED,
    ATTR_CONNECTION_TYPE,
    ATTR_DEVICE_TYPE,
    ATTR_FIRST_SEEN,
    ATTR_GUEST,
    ATTR_IPV6_ADDRESSES,
    ATTR_LAST_SEEN,
    ATTR_LEASE_TIME,
    ATTR_LINK_TYPE,
    ATTR_RSSI,
    ATTR_SIGNAL_STRENGTH,
    ATTR_WIRELESS_BAND,
    DOMAIN,
)
from .entity import BboxEntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BboxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up device tracker from a config entry."""
    coordinator: BboxDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create device tracker entities for all hosts
    entities = [BboxDeviceTracker(coordinator, host) for host in coordinator.data.hosts]

    async_add_entities(entities)


class BboxDeviceTracker(BboxEntity, ScannerEntity):
    """Representation of a Bbox device tracker."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BboxDataUpdateCoordinator, host: Host) -> None:
        """Initialize the device tracker."""
        super().__init__(coordinator)

        self._host_mac: str = host.macaddress
        self._attr_unique_id = format_mac(host.macaddress)

        # Set the name
        if host.hostname:
            self._attr_name = host.hostname
        else:
            self._attr_name = host.macaddress

        # Device info for the tracked device
        device_info = {
            "identifiers": {(DOMAIN, self._host_mac)},
            "name": self._attr_name,
            "via_device": (DOMAIN, coordinator.data.router.serialnumber),
        }

        # Add manufacturer/model if available
        if host.informations:
            if host.informations.manufacturer:
                device_info["manufacturer"] = host.informations.manufacturer
            if host.informations.model:
                device_info["model"] = host.informations.model

        self._attr_device_info = device_info

    @property
    def _host(self) -> Host | None:
        """Return the host data."""
        for host in self.coordinator.data.hosts:
            if host.macaddress == self._host_mac:
                return host
        return None

    @property
    def is_connected(self) -> bool:
        """Return true if the device is connected to the network."""
        host = self._host
        return host.active if host else False

    @property
    def source_type(self) -> SourceType:
        """Return the source type."""
        return SourceType.ROUTER

    @property
    def ip_address(self) -> str | None:
        """Return the primary IP address of the device."""
        host = self._host
        return host.ipaddress if host else None

    @property
    def mac_address(self) -> str:
        """Return the MAC address of the device."""
        return self._host_mac

    @property
    def hostname(self) -> str | None:
        """Return the hostname of the device."""
        host = self._host
        return host.hostname if host else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        host = self._host
        if not host:
            return {}

        attributes: dict[str, Any] = {
            ATTR_CONNECTION_TYPE: host.type,
            ATTR_LINK_TYPE: host.link,
        }

        # Add optional attributes
        if host.devicetype:
            attributes[ATTR_DEVICE_TYPE] = host.devicetype

        if host.firstseen:
            attributes[ATTR_FIRST_SEEN] = host.firstseen.isoformat()

        # Last seen is in seconds since last seen
        if host.lastseen is not None:
            attributes[ATTR_LAST_SEEN] = host.lastseen

        if host.guest is not None:
            attributes[ATTR_GUEST] = host.guest

        if host.lease:
            attributes[ATTR_LEASE_TIME] = host.lease

        # Wireless information
        if host.wireless:
            if host.wireless.band:
                attributes[ATTR_WIRELESS_BAND] = f"{host.wireless.band} GHz"
            if host.wireless.rssi0:
                attributes[ATTR_RSSI] = host.wireless.rssi0
                # Calculate signal strength percentage (RSSI typically -100 to -30)
                rssi = host.wireless.rssi0
                if rssi <= -100:
                    strength = 0
                elif rssi >= -30:
                    strength = 100
                else:
                    strength = int(2 * (rssi + 100))
                attributes[ATTR_SIGNAL_STRENGTH] = strength
            if host.wireless.rate:
                attributes[ATTR_CONNECTION_SPEED] = f"{host.wireless.rate} Mbps"

        # Ethernet information
        if host.ethernet and host.ethernet.speed:
            attributes[ATTR_CONNECTION_SPEED] = f"{host.ethernet.speed} Mbps"

        # IPv6 addresses
        if host.ip6address:
            ipv6_addrs = [addr.ipaddress for addr in host.ip6address]
            attributes[ATTR_IPV6_ADDRESSES] = ipv6_addrs

        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Update the name if hostname changed
        host = self._host
        if host and host.hostname:
            self._attr_name = host.hostname

        super()._handle_coordinator_update()

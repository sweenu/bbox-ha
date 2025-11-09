"""Constants for the Bouygues Telecom Bbox integration."""

from datetime import timedelta
from typing import Final

DOMAIN: Final[str] = "bbox"

# Configuration constants
CONF_BASE_URL: Final[str] = "base_url"
CONF_PASSWORD: Final[str] = "password"

# Default values
DEFAULT_BASE_URL: Final[str] = "https://mabbox.bytel.fr/api/v1/"
DEFAULT_SCAN_INTERVAL: Final[timedelta] = timedelta(seconds=30)

# Device tracker attributes
ATTR_CONNECTION_TYPE: Final[str] = "connection_type"
ATTR_LINK_TYPE: Final[str] = "link_type"
ATTR_LAST_SEEN: Final[str] = "last_seen"
ATTR_FIRST_SEEN: Final[str] = "first_seen"
ATTR_DEVICE_TYPE: Final[str] = "device_type"
ATTR_GUEST: Final[str] = "guest"
ATTR_LEASE_TIME: Final[str] = "lease_time"
ATTR_WIRELESS_BAND: Final[str] = "wireless_band"
ATTR_RSSI: Final[str] = "rssi"
ATTR_SIGNAL_STRENGTH: Final[str] = "signal_strength"
ATTR_CONNECTION_SPEED: Final[str] = "connection_speed"
ATTR_IPV6_ADDRESSES: Final[str] = "ipv6_addresses"

# Router attributes
ATTR_MODEL_NAME: Final[str] = "model_name"
ATTR_SERIAL_NUMBER: Final[str] = "serial_number"
ATTR_FIRMWARE_VERSION: Final[str] = "firmware_version"
ATTR_UPTIME: Final[str] = "uptime"
ATTR_NUMBER_OF_BOOTS: Final[str] = "number_of_boots"
ATTR_WAN_IP: Final[str] = "wan_ip"
ATTR_BANDWIDTH_UP: Final[str] = "bandwidth_up"
ATTR_BANDWIDTH_DOWN: Final[str] = "bandwidth_down"

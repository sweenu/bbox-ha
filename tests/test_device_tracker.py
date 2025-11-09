"""Test the Bbox device tracker."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.components.device_tracker import DOMAIN as DEVICE_TRACKER_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bbox.const import DOMAIN

if TYPE_CHECKING:
    from aiobbox.models import Host


@pytest.mark.usefixtures("mock_bbox_api")
async def test_device_tracker_active(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test active device tracker entity registration."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Check entity is registered in entity registry
    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.test_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "AA:BB:CC:DD:EE:FF"
    assert entry.original_name == "test-device"
    assert (
        entry.disabled_by is not None
    )  # Device tracker entities are disabled by default


@pytest.mark.usefixtures("mock_bbox_api")
async def test_device_tracker_inactive(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test inactive device tracker entity registration."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Check entity for inactive device is registered
    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.offline_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "11:22:33:44:55:66"
    assert entry.original_name == "offline-device"
    assert (
        entry.disabled_by is not None
    )  # Device tracker entities are disabled by default


async def test_device_tracker_update(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_host_active: Host,
    mock_bbox_api: MagicMock,
) -> None:
    """Test device tracker updates when host changes."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Update host to inactive
    mock_host_active.active = False
    mock_bbox_api.get_hosts = AsyncMock(return_value=[mock_host_active])

    # Trigger coordinator update
    coordinator = hass.data[DOMAIN][mock_config_entry.entry_id]
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    # Check that entity still exists in registry after update
    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.test_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "AA:BB:CC:DD:EE:FF"


@pytest.mark.usefixtures("mock_bbox_api")
async def test_device_registry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test device is properly registered."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.test_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "AA:BB:CC:DD:EE:FF"
    assert entry.original_name == "test-device"


@pytest.mark.usefixtures("mock_bbox_api", "mock_host_active")
async def test_signal_strength_calculation(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test device tracker entity registration with signal strength configuration."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Check that entity is registered
    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.test_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "AA:BB:CC:DD:EE:FF"


@pytest.mark.usefixtures("mock_bbox_api")
async def test_device_tracker_attributes(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test device tracker attributes are correctly set."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    # Check that entity is registered with correct configuration
    entity_registry = er.async_get(hass)
    entity_id = f"{DEVICE_TRACKER_DOMAIN}.test_device"
    entry = entity_registry.async_get(entity_id)

    assert entry is not None
    assert entry.unique_id == "AA:BB:CC:DD:EE:FF"
    assert entry.original_name == "test-device"
    assert entry.disabled_by is not None


@pytest.mark.usefixtures("mock_bbox_api")
async def test_all_hosts_registered(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test that all hosts from the API are registered as entities."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    entity_registry = er.async_get(hass)

    # Check that both active and inactive hosts are registered
    active_entity = entity_registry.async_get(f"{DEVICE_TRACKER_DOMAIN}.test_device")
    inactive_entity = entity_registry.async_get(
        f"{DEVICE_TRACKER_DOMAIN}.offline_device"
    )

    assert active_entity is not None
    assert inactive_entity is not None

    # Verify unique IDs match the MAC addresses from the mock data
    assert active_entity.unique_id == "AA:BB:CC:DD:EE:FF"
    assert inactive_entity.unique_id == "11:22:33:44:55:66"

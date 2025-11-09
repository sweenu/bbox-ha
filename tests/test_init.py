"""Test the Bbox init."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from aiobbox.exceptions import BboxApiError, BboxTimeoutError
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bbox.const import DOMAIN

if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.mark.usefixtures("mock_bbox_api")
async def test_setup_entry_success(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test successful setup of entry."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert DOMAIN in hass.data
    assert mock_config_entry.entry_id in hass.data[DOMAIN]


@pytest.mark.parametrize(
    ("exception", "expected_state"),
    [
        (BboxTimeoutError("Timeout", timeout=10.0), ConfigEntryState.SETUP_RETRY),
        (BboxApiError("API Error"), ConfigEntryState.SETUP_RETRY),
    ],
)
async def test_setup_entry_error(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_bbox_api: MagicMock,
    exception: Exception,
    expected_state: ConfigEntryState,
) -> None:
    """Test setup entry with errors."""
    mock_config_entry.add_to_hass(hass)
    mock_bbox_api.authenticate.side_effect = exception

    assert not await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is expected_state


async def test_unload_entry(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_bbox_api: MagicMock,
) -> None:
    """Test unloading an entry."""
    mock_config_entry.add_to_hass(hass)

    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert mock_bbox_api.close.called

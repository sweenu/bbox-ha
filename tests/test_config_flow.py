"""Test the Bbox config flow."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from aiobbox.exceptions import (
    BboxApiError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxTimeoutError,
)
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.bbox.const import CONF_BASE_URL, DOMAIN

if TYPE_CHECKING:
    from aiobbox.models import Router


pytestmark = pytest.mark.usefixtures("mock_setup_entry")


async def test_form(hass: HomeAssistant, mock_router: Router) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {}

    with patch("custom_components.bbox.config_flow.BboxApi") as mock_api:
        api_instance = mock_api.return_value
        api_instance.authenticate = AsyncMock()
        api_instance.get_router_info = AsyncMock(return_value=mock_router)
        api_instance.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_BASE_URL: "https://192.168.1.254/api/v1/",
                CONF_PASSWORD: "test_password",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == mock_router.modelname
    assert result2["data"] == {
        CONF_BASE_URL: "https://192.168.1.254/api/v1/",
        CONF_PASSWORD: "test_password",
    }


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (BboxInvalidCredentialsError("Invalid password"), "invalid_auth"),
        (BboxRateLimitError("Rate limit"), "rate_limit"),
        (BboxTimeoutError("Timeout", timeout=10.0), "cannot_connect"),
        (BboxApiError("API error"), "cannot_connect"),
        (Exception("Unknown"), "unknown"),
    ],
)
async def test_form_errors(
    hass: HomeAssistant,
    exception: Exception,
    error: str,
) -> None:
    """Test we handle errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.bbox.config_flow.BboxApi") as mock_api:
        api_instance = mock_api.return_value
        api_instance.authenticate = AsyncMock(side_effect=exception)
        api_instance.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_BASE_URL: "https://192.168.1.254/api/v1/",
                CONF_PASSWORD: "wrong_password",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": error}


async def test_form_already_configured(
    hass: HomeAssistant,
    mock_config_entry: config_entries.ConfigEntry,
    mock_router: Router,
) -> None:
    """Test we abort if already configured."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch("custom_components.bbox.config_flow.BboxApi") as mock_api:
        api_instance = mock_api.return_value
        api_instance.authenticate = AsyncMock()
        api_instance.get_router_info = AsyncMock(return_value=mock_router)
        api_instance.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_BASE_URL: "https://192.168.1.254/api/v1/",
                CONF_PASSWORD: "test_password",
            },
        )

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_reauth_flow(
    hass: HomeAssistant,
    mock_config_entry: config_entries.ConfigEntry,
    mock_router: Router,
) -> None:
    """Test reauth flow."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    with patch("custom_components.bbox.config_flow.BboxApi") as mock_api:
        api_instance = mock_api.return_value
        api_instance.authenticate = AsyncMock()
        api_instance.get_router_info = AsyncMock(return_value=mock_router)
        api_instance.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "new_password"},
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reauth_successful"


@pytest.mark.parametrize(
    ("exception", "error"),
    [
        (BboxInvalidCredentialsError("Invalid password"), "invalid_auth"),
        (BboxTimeoutError("Timeout", timeout=10.0), "cannot_connect"),
    ],
)
async def test_reauth_flow_errors(
    hass: HomeAssistant,
    mock_config_entry: config_entries.ConfigEntry,
    exception: Exception,
    error: str,
) -> None:
    """Test reauth flow with errors."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_REAUTH,
            "entry_id": mock_config_entry.entry_id,
        },
        data=mock_config_entry.data,
    )

    with patch("custom_components.bbox.config_flow.BboxApi") as mock_api:
        api_instance = mock_api.return_value
        api_instance.authenticate = AsyncMock(side_effect=exception)
        api_instance.close = AsyncMock()

        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_PASSWORD: "wrong_password"},
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": error}

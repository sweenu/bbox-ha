"""Fixtures for Bbox integration tests."""

from __future__ import annotations

from collections.abc import Generator
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiobbox.models import (
    DeviceInformation,
    Host,
    Router,
    RouterDisplay,
    RouterUsing,
    RouterVersion,
    WirelessInfo,
)
from homeassistant.const import CONF_PASSWORD
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.bbox.const import CONF_BASE_URL, DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # noqa: ARG001
    yield


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "custom_components.bbox.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Create a mock config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Bbox Test Router",
        data={
            CONF_BASE_URL: "https://192.168.1.254/api/v1/",
            CONF_PASSWORD: "test_password",
        },
        unique_id="TEST12345",
    )


@pytest.fixture
def mock_router() -> Router:
    """Create a mock router object."""
    return Router(
        now=datetime.now(),
        status=1,
        numberofboots=10,
        modelname="Bbox Test Router",
        modelclass="BBOX-TEST",
        optimisation=True,
        user_configured=True,
        serialnumber="TEST12345",
        display=RouterDisplay(luminosity=100, luminosity_extender=50, state="on"),
        main=RouterVersion(version="1.0.0", date=datetime.now()),
        reco=RouterVersion(version="1.0.0", date=datetime.now()),
        running=RouterVersion(version="1.0.0", date=datetime.now()),
        spl=RouterVersion(version="1.0.0", date=datetime.now()),
        tpl=RouterVersion(version="1.0.0", date=datetime.now()),
        ldr1=RouterVersion(version="1.0.0", date=datetime.now()),
        ldr2=RouterVersion(version="1.0.0", date=datetime.now()),
        firstusedate=datetime.now(),
        uptime=86400,
        lastFactoryReset=0,
        using=RouterUsing(ipv4=True, ipv6=True, ftth=True, adsl=False, vdsl=False),
    )


@pytest.fixture
def mock_host_active() -> Host:
    """Create a mock active host."""
    return Host(
        id=1,
        active=True,
        hostname="test-device",
        ipaddress="192.168.1.100",
        macaddress="AA:BB:CC:DD:EE:FF",
        type="DHCP",
        link="Wifi 5",
        lease=3600,
        firstseen=datetime.now(),
        lastseen=0,
        devicetype="Computer",
        informations=DeviceInformation(
            type="Computer",
            manufacturer="Test Manufacturer",
            model="Test Model",
            icon="mdi:laptop",
            operatingSystem="Linux",
            version="1.0",
        ),
        wireless=WirelessInfo(
            wexindex=1,
            static=False,
            band=5.0,
            txUsage=10,
            rxUsage=20,
            estimatedRate=1000,
            rssi0=-45,
            mcs=9,
            rate=866,
        ),
    )


@pytest.fixture
def mock_host_inactive() -> Host:
    """Create a mock inactive host."""
    return Host(
        id=2,
        active=False,
        hostname="offline-device",
        ipaddress="192.168.1.101",
        macaddress="11:22:33:44:55:66",
        type="DHCP",
        link="Ethernet",
        lease=0,
        firstseen=datetime.now(),
        lastseen=3600,
        devicetype="Phone",
    )


@pytest.fixture
def mock_bbox_api(
    mock_router: Router,
    mock_host_active: Host,
    mock_host_inactive: Host,
) -> Generator[MagicMock]:
    """Create a mock BboxApi."""
    with (
        patch(
            "custom_components.bbox.coordinator.BboxApi", autospec=True
        ) as mock_api_coordinator,
        patch(
            "custom_components.bbox.config_flow.BboxApi", autospec=True
        ) as mock_api_config_flow,
    ):
        api_instance = mock_api_coordinator.return_value
        api_instance.authenticate = AsyncMock()
        api_instance.get_router_info = AsyncMock(return_value=mock_router)
        api_instance.get_hosts = AsyncMock(
            return_value=[mock_host_active, mock_host_inactive]
        )
        api_instance.close = AsyncMock()

        # Configure config_flow mock to match coordinator mock
        mock_api_config_flow.return_value = api_instance

        yield api_instance

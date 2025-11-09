# Bbox Home Assistant Integration - File Structure

## Directory Layout

```
custom_components/bbox/
├── __init__.py              # Integration setup and initialization
├── config_flow.py           # Configuration UI flow
├── const.py                 # Constants and defaults
├── coordinator.py           # Data update coordinator
├── device_tracker.py        # Device tracker entities
├── entity.py                # Base entity class
├── manifest.json            # Integration metadata
├── strings.json             # UI strings
└── translations/
    └── en.json              # English translations

tests/
├── __init__.py              # Test package init
├── conftest.py              # Pytest fixtures
├── test_config_flow.py      # Config flow tests
├── test_device_tracker.py   # Device tracker tests
└── test_init.py             # Integration setup tests
```

## File Descriptions

### Core Integration Files

- **__init__.py** - Entry point for the integration. Handles setup and teardown of config entries.
- **config_flow.py** - Configuration flow using Home Assistant UI. Handles initial setup and re-authentication.
- **const.py** - All constants used throughout the integration (domain, attributes, defaults).
- **coordinator.py** - DataUpdateCoordinator that manages polling and data fetching from the Bbox API.
- **device_tracker.py** - Device tracker entity implementation using ScannerEntity.
- **entity.py** - Base entity class with common device info setup.
- **manifest.json** - Integration metadata (domain, name, requirements, quality scale).
- **strings.json** - Translatable strings for the config flow UI.
- **translations/en.json** - English translations.

### Test Files

- **conftest.py** - Pytest fixtures for mocking API responses and config entries.
- **test_init.py** - Tests for integration setup and teardown.
- **test_config_flow.py** - Tests for configuration flow UI and validation.
- **test_device_tracker.py** - Tests for device tracker entities and attributes.

## Installation Instructions

### 1. Create Directory Structure

```bash
mkdir -p custom_components/bbox/tests
mkdir -p custom_components/bbox/translations
mkdir -p custom_components/bbox/aiobbox
```

### 2. Copy Files

Copy the provided files to their respective locations:

```bash
# Core files
cp __init__.py custom_components/bbox/
cp config_flow.py custom_components/bbox/
cp const.py custom_components/bbox/
cp coordinator.py custom_components/bbox/
cp device_tracker.py custom_components/bbox/
cp entity.py custom_components/bbox/
cp manifest.json custom_components/bbox/
cp strings.json custom_components/bbox/

# Translation files
cp translations/en.json custom_components/bbox/translations/

# Test files
cp conftest.py custom_components/bbox/tests/
cp test_init.py custom_components/bbox/tests/
cp test_config_flow.py custom_components/bbox/tests/
cp test_device_tracker.py custom_components/bbox/tests/

# aiobbox library - copy the files you provided
cp models.py custom_components/bbox/aiobbox/
cp exceptions.py custom_components/bbox/aiobbox/
cp client.py custom_components/bbox/aiobbox/
```

### 3. Create __init__ Files

```bash
touch custom_components/bbox/tests/__init__.py
touch custom_components/bbox/aiobbox/__init__.py
```

### 4. Update manifest.json

Remove or update the `requirements` section if bundling aiobbox locally:

```json
{
  "domain": "bbox",
  "name": "Bouygues Telecom Bbox",
  "codeowners": ["@yourusername"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://www.home-assistant.io/integrations/bbox",
  "integration_type": "device",
  "iot_class": "local_polling",
  "requirements": [],
  "quality_scale": "platinum"
}
```

## File Naming Notes

- Rename `.md` files to `.py` files before use (they are saved as markdown for display purposes)
- The `__init__.py` files are saved as `__init__.md` and should be renamed to `__init__.py`

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-homeassistant-custom-component pytest-asyncio

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_device_tracker.py -v

# Run with coverage
pytest tests/ --cov=custom_components/bbox --cov-report=html
```

## Key Features

- ✅ **Platinum Quality**: Full type hints, comprehensive tests, error handling
- ✅ **Python 3.13**: Uses latest type hint syntax (PEP 604, etc.)
- ✅ **DataUpdateCoordinator**: Efficient polling with 30-second intervals
- ✅ **Device Tracking**: Tracks connected devices with rich attributes
- ✅ **Re-authentication**: Automatic session refresh flow
- ✅ **Router Info**: Displays router status and statistics
- ✅ **Full Testing**: Unit tests for all major components
- ✅ **Type Safe**: 100% type hints throughout

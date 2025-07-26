"""Custom types for homeassistant_geizhals_integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import GeizhalsIntegrationApiClient
    from .coordinator import GeizhalsIntegrationDataUpdateCoordinator


type GeizhalsIntegrationConfigEntry = ConfigEntry[GeizhalsIntegrationData]


@dataclass
class GeizhalsIntegrationData:
    """Data for the Blueprint integration."""

    client: GeizhalsIntegrationApiClient
    coordinator: GeizhalsIntegrationDataUpdateCoordinator
    integration: Integration

"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import GeizhalsIntegrationDataUpdateCoordinator


class GeizhalsIntegrationEntity(CoordinatorEntity[GeizhalsIntegrationDataUpdateCoordinator]):
    """BlueprintEntity class."""

    def __init__(self, coordinator: GeizhalsIntegrationDataUpdateCoordinator, id_suffix: str) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id + id_suffix
        self._attr_device_info = DeviceInfo(
            name=coordinator.data.get("name"),
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
        )

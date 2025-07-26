"""Sensor platform for geizhals_integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CURRENCY_EURO

from .entity import GeizhalsIntegrationEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import GeizhalsIntegrationDataUpdateCoordinator
    from .data import GeizhalsIntegrationConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: GeizhalsIntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        [
            GeizhalsIntegrationSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=SensorEntityDescription(
                    key="geizhals_integration_min_price",
                    name="Current minimum price",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=CURRENCY_EURO,
                    suggested_display_precision=2,
                    icon="mdi:currency-eur",
                ),
                data_key="min_price",
            ),
            GeizhalsIntegrationSensor(
                coordinator=entry.runtime_data.coordinator,
                entity_description=SensorEntityDescription(
                    key="geizhals_integration_max_price",
                    name="Current maximum price",
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=CURRENCY_EURO,
                    suggested_display_precision=2,
                    icon="mdi:currency-eur",
                ),
                data_key="max_price",
            ),
        ]
    )


class GeizhalsIntegrationSensor(GeizhalsIntegrationEntity, SensorEntity):
    """geizhals_integration Sensor class."""

    def __init__(
        self,
        coordinator: GeizhalsIntegrationDataUpdateCoordinator,
        entity_description: SensorEntityDescription,
        data_key: str,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, data_key)
        self.entity_description = entity_description
        self.data_key = data_key

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        return self.coordinator.data.get(self.data_key)

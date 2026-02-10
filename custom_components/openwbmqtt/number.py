"""Support for openWB MQTT numbers."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, NUMBER_TYPES
from .coordinator import OpenWBMqttDataUpdateCoordinator
from .models import OpenWBMqttEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up openWB MQTT number entities."""
    coordinator: OpenWBMqttDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        OpenWBMqttNumber(coordinator, description)
        for description in NUMBER_TYPES
        if description.exists_fn(coordinator.data)
    ]
    async_add_entities(entities)


class OpenWBMqttNumber(CoordinatorEntity, NumberEntity):
    """Representation of an openWB MQTT number."""

    entity_description: OpenWBMqttEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenWBMqttDataUpdateCoordinator,
        description: OpenWBMqttEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_value = description.value_fn(coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value_fn(self.coordinator.data)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value via MQTT service call."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        payload = str(int(value))

        # Korrekter Service Call über self.hass
        await self.hass.services.async_call(
            "mqtt",
            "publish",
            {
                "topic": topic,
                "payload": payload,
                "retain": False
            },
        )
        
        # Lokalen State sofort aktualisieren für besseres UI-Feedback
        self._attr_native_value = value
        self.async_write_ha_state()

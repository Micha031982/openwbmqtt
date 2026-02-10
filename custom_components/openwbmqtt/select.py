"""Support for openWB MQTT selects."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SELECT_TYPES
from .coordinator import OpenWBMqttDataUpdateCoordinator
from .models import OpenWBMqttEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up openWB MQTT select entities."""
    coordinator: OpenWBMqttDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        OpenWBMqttSelect(coordinator, description)
        for description in SELECT_TYPES
        if description.exists_fn(coordinator.data)
    ]
    async_add_entities(entities)


class OpenWBMqttSelect(CoordinatorEntity, SelectEntity):
    """Representation of an openWB MQTT select."""

    entity_description: OpenWBMqttEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenWBMqttDataUpdateCoordinator,
        description: OpenWBMqttEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = coordinator.device_info
        self._attr_options = list(description.payload_dict.keys())
        self._attr_current_option = description.value_fn(coordinator.data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_current_option = self.entity_description.value_fn(
            self.coordinator.data
        )
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Update the current value via MQTT service call."""
        topic = self.entity_description.mqttTopicCommand
        payload = self.entity_description.payload_dict.get(option)

        # Umstellung auf den asynchronen Service Call
        await self.hass.services.async_call(
            "mqtt",
            "publish",
            {
                "topic": topic,
                "payload": payload,
                "retain": False
            },
        )
        
        self._attr_current_option = option
        self.async_write_ha_state()

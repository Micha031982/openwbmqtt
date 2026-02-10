"""Support for openWB MQTT switches."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SWITCH_TYPES
from .coordinator import OpenWBMqttDataUpdateCoordinator
from .models import OpenWBMqttEntityDescription

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up openWB MQTT switch entities."""
    coordinator: OpenWBMqttDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        OpenWBMqttSwitch(coordinator, description)
        for description in SWITCH_TYPES
        if description.exists_fn(coordinator.data)
    ]
    async_add_entities(entities)


class OpenWBMqttSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an openWB MQTT switch."""

    entity_description: OpenWBMqttEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenWBMqttDataUpdateCoordinator,
        description: OpenWBMqttEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{description.key}"
        self._attr_device_info = coordinator.device_info
        self._attr_is_on = bool(description.value_fn(coordinator.data))

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_is_on = bool(self.entity_description.value_fn(self.coordinator.data))
        self.async_write_ha_state()

    def publishToMQTT(self):
        """Publish data to MQTT using the internal service call."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        payload = str(int(self._attr_is_on))

        # Hier die wichtige Änderung auf self.hass.services.call
        self.hass.services.call(
            "mqtt",
            "publish",
            {
                "topic": topic,
                "payload": payload,
                "retain": False
            },
        )

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        self._attr_is_on = True
        self.publishToMQTT()
        self.async_write_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        self._attr_is_on = False
        self.publishToMQTT()
        self.async_write_ha_state()

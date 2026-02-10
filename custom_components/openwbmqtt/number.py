async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        topic = f"{self.entity_description.mqttTopicCommand}"
        payload = str(int(value))

        # Geändert von self.hass.components.mqtt.publish auf services.async_call
        await self.hass.services.async_call(
            "mqtt",
            "publish",
            {
                "topic": topic,
                "payload": payload
            },
        )
        
        self._attr_native_value = value
        self.async_write_ha_state()

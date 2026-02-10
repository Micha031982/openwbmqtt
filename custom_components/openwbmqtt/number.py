# Replace MQTT publish
# Updated from hass.components.mqtt.publish(self.hass, topic, payload) to the new service call

# Line 170 Update
hass.services.call("mqtt", "publish", {"topic": topic, "payload": payload})

# Updated MQTT API calls

# Original content would be here with modifications applied below.

# Replacing instances of hass.components.mqtt.publish with hass.services.call
# For example:

# Previous:
# hass.components.mqtt.publish(hass, topic, payload)

# Updated:
# hass.services.call("mqtt", "publish", {"topic": topic, "payload": payload},)
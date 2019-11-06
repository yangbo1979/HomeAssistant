# HomeAssistant
home assistant custom components
The iMeter integration connects home-assistant to iMeter power meters. iMeters may be connected to a home Wi-Fi network and expose a REST API.

Configuration

To use the sensors in your installation, add the following to your configuration.yaml file:

# Example configuration.yaml entry
sensor:
  - platform: imeter
    host: IP_ADDRESS

CONFIGURATION VARIABLES

host
(string)(Required)
The IP address of your iMeter system.

model
(string)(Optional，auto recognize as default)
WEM3162 WEM3080 WEM3080T

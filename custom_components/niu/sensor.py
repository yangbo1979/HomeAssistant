"""Support for the Niu sensors."""
import logging
import asyncio
from datetime import timedelta
from homeassistant.const import (
    LENGTH_KILOMETERS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval

from . import DOMAIN as NIU_DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=600)

sensor_map = {
    "totalPoint":("骑行次数","times"),
    "batteryCharging":("电量","%"),
    "isConnected":("连接",""),
    "temperature":("温度","℃"),
    "chargedTimes":("充电次数","times"),
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Niu sensor platform."""
    controller = hass.data[NIU_DOMAIN]["controller"]
    devices = []
    #_LOGGER.error(hass.data[NIU_DOMAIN])
    for sensor_id in sensor_map:
        #_LOGGER.error(sensor_id+sensor_map[sensor_id][0]+sensor_map[sensor_id][1])
        devices.append(NiuSensor(controller,sensor_id,sensor_map[sensor_id][0],sensor_map[sensor_id][1]))
    
    endpoint = RealTimeDataEndpoint(hass, controller)
    endpoint.sensors = devices
    hass.async_add_job(endpoint.async_refresh)
    async_track_time_interval(hass, endpoint.async_refresh, SCAN_INTERVAL)
    async_add_entities(devices, True)

class NiuSensor(Entity):
    """Representation of Niu sensors."""

    def __init__(self, controller, sensor_id,sensor_name,sensor_unit):
        """Initialize of the sensor."""
        self._controller = controller
        self.current_value = None
        self._sensorid = sensor_id
        self._unit = sensor_unit
        self.last_changed_time = None
        self._sensorname = sensor_name
        self._uid = f"{self._controller._sn}_{self._sensorid}"

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        #_LOGGER.error(self._uid)
        return self._uid

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.current_value

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._unit

    @property
    def should_poll(self):
        """No polling needed."""
        return False   

    @property
    def name(self):
        return f"{self._sensorname}"
        #return self._uid




class RealTimeDataEndpoint:
    """Representation of a Sensor."""

    def __init__(self, hass, niuIns):
        """Initialize the sensor."""
        self.hass = hass
        self.scooter = niuIns
        self.ready = asyncio.Event()
        self.sensors = []

    async def async_refresh(self, now=None):
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        #_LOGGER.error("refresh endpoint")
        try:
            #self.scooter.get_vehicles(self.scooter._token)
            self.scooter.get_battery_info()
            self.ready.set()
        except:
            if now is not None:
                self.ready.clear()
                return
            raise PlatformNotReady
        data = self.scooter._batteryInfo
        #_LOGGER.error(data)
        for sensor in self.sensors:
            if sensor._sensorid in data:
                sensor.current_value = data[sensor._sensorid]
                sensor.async_added_to_hass()
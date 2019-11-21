"""Support for tracking Tesla cars."""
import logging

from homeassistant.helpers.event import async_track_utc_time_change
from homeassistant.util import slugify

from . import DOMAIN as NIU_DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_scanner(hass, config, async_see, discovery_info=None):
    """Set up the Niu tracker."""
    _LOGGER.error("setup device tracker")
    controller = hass.data[NIU_DOMAIN]["controller"]
    tracker = NiuDeviceTracker(
        hass, config, async_see,controller
    )
    await tracker.update_info()
    async_track_utc_time_change(hass, tracker.update_info, second=59)
    return True

class NiuDeviceTracker:
    """A class representing a Niu device."""
    def __init__(self, hass, config, see,controller):
        """Initialize the Niu device scanner."""
        self.hass = hass
        self.see = see
        self._controller = controller
        self._uid = f"{self._controller._sn}_gps"

    async def update_info(self, now=None):
        """Update the device info."""
        _LOGGER.error("update device tracker")
        self._controller.get_motor_info()
        _LOGGER.error(self._controller._motorInfo)
        lat = self._controller._motorInfo["postion"]['lat']
        lon = self._controller._motorInfo["postion"]['lng']
        name = "GPS"
        dev_id = slugify(self._uid)
        attrs = {"trackr_id": dev_id, "id": dev_id, "name": name}
        await self.see(
            dev_id=dev_id, host_name=name, gps=(lat, lon), attributes=attrs
        )
        #_LOGGER.error(lat)
        '''
        for device in self.devices:
            await device.async_update()
            name = device.name
            _LOGGER.debug("Updating device position: %s", name)
            dev_id = slugify(device.uniq_name)
            location = device.get_location()
            if location:
                lat = location["latitude"]
                lon = location["longitude"]
                attrs = {"trackr_id": dev_id, "id": dev_id, "name": name}
                await self.see(
                    dev_id=dev_id, host_name=name, gps=(lat, lon), attributes=attrs
                )
        '''
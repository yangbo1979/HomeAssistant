from collections import defaultdict
import logging
import voluptuous as vol
from .const import DOMAIN, NIU_COMPONENTS
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_EMAIL,
)
from homeassistant.exceptions import PlatformNotReady
from homeassistant.helpers import aiohttp_client, config_validation as cv, discovery
from homeassistant.helpers.entity import Entity
from homeassistant.util import slugify
_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_EMAIL): cv.string,
                vol.Required(CONF_PASSWORD): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=300): vol.All(
                    cv.positive_int, vol.Clamp(min=300)
                ),
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
async def async_setup(hass, base_config):
    from niu_scooter import niu
    config = base_config.get(DOMAIN)

    email = config.get(CONF_EMAIL)
    password = config.get(CONF_PASSWORD)
    update_interval = config.get(CONF_SCAN_INTERVAL)
    my_scooter = None
    if hass.data.get(DOMAIN) is None:
        try:
            my_scooter = niu.Scooter(email,password)
            hass.data[DOMAIN] = {"controller": my_scooter, "devices": defaultdict(list)}
            _LOGGER.info("[Success]connect to Niu server")
            my_scooter.get_battery_info()
            #_LOGGER.error(my_scooter._batteryInfo)
        except:
            _LOGGER.error("[FAIL]to connect to Niu server")

    # Return boolean to indicate that initialization was successful.
    for component in NIU_COMPONENTS:
        hass.async_create_task(
            discovery.async_load_platform(hass, component, DOMAIN, {}, base_config)
        )
    return True
	
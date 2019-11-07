"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
import logging

_LOGGER = logging.getLogger(__name__)

CONF_HOST = 'host'
CONF_MODEL = 'model'
CONF_NAME = 'name'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_MODEL, default='WEM3080'): cv.string,
    vol.Optional(CONF_NAME, default='iMeter'): cv.string
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the sensor platform."""
    '''
    _LOGGER.error(config['model'])
    if config['model'] == 'WEM3162':
    	print('WEM3162')
    if config['model'] == 'WEM3080':
    	print('wem3080')
    if config['model'] == 'WEM3080T':
    	print('WEM3080T')
    '''
    add_entities([IamMeterSensor(hass, config)])


class IamMeterSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, hass, config):
        """Initialize the sensor."""
        try:
        	self._model = config["model"]
        except:
        	_LOGGER.error("model not set:WEM3162，WEM3080，WEM3080T，default to WEM3080")
        	self._model = "WEM3080"
        try:
        	self._host = config["host"]
        except:
        	_LOGGER.error("host not set")
        self._state = None
        self._data = None
        self._name = config[CONF_NAME]
        self._hass = hass
        self._hass.custom_attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_class(self):
        return 'power'
        
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""
        return 'W'
        
    @property
    def data(self):
        return self._data
    
    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        return self._hass.custom_attributes

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        import requests
        import json
        from requests.compat import urljoin
        
        attributes = {}
        dev_ip = self._host
        base_url = urljoin('http://admin:admin@'+dev_ip, '/monitorjson')
        try:
        	r = requests.get(base_url)
        	json_response = json.loads(r.text)
        	'''
        	if self._model == 'WEM3162':
        		#print('WEM3162')
        		self._data = json_response['data']
        		self._state = self._data[2]
        	if self._model == 'WEM3080':
        		#print('WEM3080')
        		self._data = json_response['Data']
        		self._state = self._data[2]
        	if self._model == 'WEM3080T':
        		#print('WEM3080T')
        		self._data = json_response['Datas']
        		self._state = self._data[0][2]+self._data[1][2]+self._data[2][2]
        	'''
        	try:
        		self._data = json_response['data']
        		self._state = self._data[2]
        	except:
        		#_LOGGER.error('not 3162')
        		try:
        			self._data = json_response['Data']
        			self._state = self._data[2]
        		except:
        			#_LOGGER.error('not 3080')
        			try:
        				self._data = json_response['Datas']
        				self._state = self._data[0][2]+self._data[1][2]+self._data[2][2]
        			except:
        				_LOGGER.error('unrecognizable device')
        				pass
        			pass
        		pass
        	attributes['data'] = self._data
        	try:
        		attributes['mac'] = json_response['mac']
        	except:
        		pass
        	try:
        		attributes['sn'] = json_response['SN']
        	except:
        		pass
        	self._hass.custom_attributes = attributes
        except requests.exceptions.RequestException as e:
        	self._state = 'offline'
        

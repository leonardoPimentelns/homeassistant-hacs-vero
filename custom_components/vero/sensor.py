
"""Verointernet component for Home Assistant"""

DOMAIN = 'verointernet'
ATTR_CONTRATOS = 'contratos'
ATTR_VELOCIDADE = 'velocidade'
ATTR_STATUS_CONEXAO = 'statusConexao'
ATTR_FATURAS = 'faturas'

import logging
import voluptuous as vol

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

from .verointernet_api import get_access_token, get_invoice_details

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required('username'): cv.string,
        vol.Required('password'): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)

def setup_platform(hass, config, add_entities, discovery_info=None):
    username = config[DOMAIN]['username']
    password = config[DOMAIN]['password']
    access_token = get_access_token(username, password)
    if access_token is None:
        _LOGGER.error("Failed to retrieve access token")
        return

    data = get_invoice_details(access_token)
    if data is None:
        _LOGGER.error("Failed to retrieve invoice details")
        return

    entities = []
    entities.append(VerointernetEntity(data, ATTR_VELOCIDADE, 'Velocidade'))
    entities.append(VerointernetEntity(data, ATTR_STATUS_CONEXAO, 'Status de Conexão'))
    for i, contrato in enumerate(data[ATTR_CONTRATOS]):
        entities.append(VerointernetEntity(contrato, 'valor', f'Contrato {i+1} - Valor'))
        entities.append(VerointernetEntity(contrato, 'diaVencimento', f'Contrato {i+1} - Dia de Vencimento'))
    entities.append(VerointernetEntity(data[ATTR_FATURAS], 'valor', 'Fatura Atual'))
    entities.append(VerointernetEntity(data[ATTR_FATURAS], 'dataVencimento', 'Fatura Atual - Vencimento'))

    add_entities(entities, True)

class VerointernetEntity(Entity):
    def __init__(self, data, attribute, name):
        self._data = data
        self._attribute = attribute
        self._name = name
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        return False

    def update(self):
        self._state = self._data.get(self._attribute)

    @property
    def device_state_attributes(self):
        return self._data

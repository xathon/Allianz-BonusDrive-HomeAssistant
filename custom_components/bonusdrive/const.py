"""Constants for bonusdrive."""

from logging import Logger, getLogger

LOGGER: Logger = getLogger(__package__)

DOMAIN = "bonusdrive"
ATTRIBUTION = "Data provided by Allianz BonusDrive"

# Configuration constants
CONF_BASE_URL = "base_url"
CONF_PHOTON_URL = "photon_url"
DEFAULT_BASE_URL = "https://bonusdrive.drivesync.com"

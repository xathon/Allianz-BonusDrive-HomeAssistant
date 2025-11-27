"""BonusdriveEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import BonusdriveDataUpdateCoordinator


class BonusdriveEntity(CoordinatorEntity[BonusdriveDataUpdateCoordinator]):
    """BonusdriveEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(self, coordinator: BonusdriveDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    coordinator.config_entry.entry_id,
                ),
            },
            name="BonusDrive",
            manufacturer="Allianz",
            model="BonusDrive",
        )

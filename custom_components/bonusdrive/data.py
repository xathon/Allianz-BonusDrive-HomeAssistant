"""Custom types for bonusdrive."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from allianz_bonusdrive_client import Badge, Scores, Trip
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import BonusdriveApiClient
    from .coordinator import BonusdriveDataUpdateCoordinator


type BonusdriveConfigEntry = ConfigEntry[BonusdriveData]


@dataclass
class BonusdriveData:
    """Data for the Bonusdrive integration."""

    client: BonusdriveApiClient
    coordinator: BonusdriveDataUpdateCoordinator
    integration: Integration


@dataclass
class BonusdriveCoordinatorData:
    """Data returned by the coordinator."""

    last_trip: Trip | None = None
    daily_badge: Badge | None = None
    monthly_badge: Badge | None = None
    daily_scores: Scores | None = None

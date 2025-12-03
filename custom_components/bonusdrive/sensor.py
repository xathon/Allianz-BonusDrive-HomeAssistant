"""Sensor platform for bonusdrive."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)

from .const import CONF_PHOTON_URL
from .entity import BonusdriveEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BonusdriveDataUpdateCoordinator
    from .data import BonusdriveConfigEntry


# Medal level mapping: level -> translation key
MEDAL_LEVELS: dict[int, str] = {
    1: "gold",
    2: "silver",
    3: "bronze",
    5: "red",
}
DEFAULT_MEDAL = "none"

# Minimum number of coordinates needed for lat/lon pair
MIN_COORD_LENGTH = 2


def get_medal_for_level(level: int) -> str:
    """Get the medal translation key for a badge level."""
    return MEDAL_LEVELS.get(level, DEFAULT_MEDAL)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: BonusdriveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator

    entities: list[SensorEntity] = [
        LastTripSensor(coordinator),
        DailyBadgeSensor(coordinator),
        MonthlyBadgeSensor(coordinator),
    ]

    async_add_entities(entities)


class LastTripSensor(BonusdriveEntity, SensorEntity):
    """Sensor for the last trip with detailed attributes."""

    _attr_translation_key = "last_trip"
    _attr_icon = "mdi:car-connected"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: BonusdriveDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_last_trip"

    @property
    def native_value(self) -> int | None:
        """Return the overall score of the last trip."""
        if self.coordinator.data and self.coordinator.data.last_trip:
            return int(self.coordinator.data.last_trip.tripScore)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return detailed trip attributes."""
        if not self.coordinator.data or not self.coordinator.data.last_trip:
            return None

        trip = self.coordinator.data.last_trip
        scores = trip.tripScores.scores if trip.tripScores else None

        # Format duration as h:mm:ss
        hours, remainder = divmod(trip.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"

        attrs: dict[str, Any] = {
            "distance_km": round(trip.kilometers, 2),
            "duration": duration_str,
            "driven_by": trip.user.publicDisplayName if trip.user else None,
            "avg_speed_kmh": round(trip.avgKilometersPerHour, 1),
            "max_speed_kmh": round(trip.maxKilometersPerHour, 1),
            "start_time": datetime.fromtimestamp(
                trip.tripStartTimestampUtc / 1000, tz=UTC
            ).isoformat(),
            "end_time": datetime.fromtimestamp(
                trip.tripEndTimestampUtc / 1000, tz=UTC
            ).isoformat(),
        }

        # Add start/end coordinates from decoded_geometry if available
        decoded_geometry = getattr(trip, "decoded_geometry", None)
        if decoded_geometry and len(decoded_geometry) >= MIN_COORD_LENGTH:
            start_point = decoded_geometry[0]
            end_point = decoded_geometry[-1]
            if start_point and len(start_point) >= MIN_COORD_LENGTH:
                lat_dir = "N" if start_point[0] >= 0 else "S"
                lon_dir = "E" if start_point[1] >= 0 else "W"
                attrs["start_latitude"] = f"{lat_dir} {abs(start_point[0]):.6f}"
                attrs["start_longitude"] = f"{lon_dir} {abs(start_point[1]):.6f}"
            if end_point and len(end_point) >= MIN_COORD_LENGTH:
                lat_dir = "N" if end_point[0] >= 0 else "S"
                lon_dir = "E" if end_point[1] >= 0 else "W"
                attrs["end_latitude"] = f"{lat_dir} {abs(end_point[0]):.6f}"
                attrs["end_longitude"] = f"{lon_dir} {abs(end_point[1]):.6f}"

        # Add location strings if available (from Photon geocoding)
        if self.coordinator.config_entry.data.get(CONF_PHOTON_URL):
            if hasattr(trip, "start_point_string") and trip.start_point_string:
                attrs["start_location"] = trip.start_point_string
            if hasattr(trip, "end_point_string") and trip.end_point_string:
                attrs["end_location"] = trip.end_point_string

        # Add detailed scores if available
        if scores:
            attrs["speeding_score"] = round(scores.speeding, 1)
            attrs["harsh_braking_score"] = round(scores.harsh_braking, 1)
            attrs["harsh_acceleration_score"] = round(scores.harsh_acceleration, 1)
            attrs["harsh_cornering_score"] = round(scores.harsh_cornering, 1)
            attrs["payd_score"] = round(scores.payd, 1)

        return attrs


class DailyBadgeSensor(BonusdriveEntity, SensorEntity):
    """Sensor for the current daily score with badge info."""

    _attr_translation_key = "daily_badge"
    _attr_icon = "mdi:medal"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: BonusdriveDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_daily_badge"

    @property
    def native_value(self) -> str | None:
        """Return the overall daily score."""
        if self.coordinator.data and self.coordinator.data.daily_scores:
            return str(self.coordinator.data.daily_scores.overall)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return badge and score attributes."""
        if not self.coordinator.data:
            return None

        attrs: dict[str, Any] = {}

        # Add detailed scores if available
        scores = self.coordinator.data.daily_scores
        if scores:
            attrs["speeding_score"] = round(scores.speeding, 1)
            attrs["harsh_braking_score"] = round(scores.harsh_braking, 1)
            attrs["harsh_acceleration_score"] = round(scores.harsh_acceleration, 1)
            attrs["harsh_cornering_score"] = round(scores.harsh_cornering, 1)
            attrs["payd_score"] = round(scores.payd, 1)
            attrs["mileage"] = round(scores.mileage, 1)

        # Add badge info if available
        badge = self.coordinator.data.daily_badge
        if badge:
            attrs["level"] = badge.level
            attrs["medal"] = get_medal_for_level(badge.level)
            attrs["points_awarded"] = badge.pointsAwarded
            attrs["badge_state"] = badge.state
            attrs["date"] = datetime.fromtimestamp(badge.date / 1000, tz=UTC).strftime(
                "%Y-%m-%d"
            )

        return attrs if attrs else None


class MonthlyBadgeSensor(BonusdriveEntity, SensorEntity):
    """Sensor for the current monthly badge."""

    _attr_translation_key = "monthly_badge"
    _attr_icon = "mdi:trophy"

    def __init__(self, coordinator: BonusdriveDataUpdateCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_monthly_badge"

    @property
    def native_value(self) -> str | None:
        """Return the medal type for the monthly badge."""
        if self.coordinator.data and self.coordinator.data.monthly_badge:
            return get_medal_for_level(self.coordinator.data.monthly_badge.level)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return badge attributes."""
        if not self.coordinator.data or not self.coordinator.data.monthly_badge:
            return None

        badge = self.coordinator.data.monthly_badge

        attrs: dict[str, Any] = {
            "level": badge.level,
            "points_awarded": badge.pointsAwarded,
            "badge_state": badge.state,
            "month": datetime.fromtimestamp(badge.date / 1000, tz=UTC).strftime(
                "%B %Y"
            ),
        }

        return attrs

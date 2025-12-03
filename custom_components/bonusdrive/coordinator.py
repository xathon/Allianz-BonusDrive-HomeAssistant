"""DataUpdateCoordinator for bonusdrive."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import (
    BonusdriveApiClientAuthenticationError,
    BonusdriveApiClientError,
)
from .data import BonusdriveCoordinatorData

if TYPE_CHECKING:
    from .data import BonusdriveConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class BonusdriveDataUpdateCoordinator(DataUpdateCoordinator[BonusdriveCoordinatorData]):
    """Class to manage fetching data from the API."""

    config_entry: BonusdriveConfigEntry

    async def _async_update_data(self) -> BonusdriveCoordinatorData:
        """Update data via library."""
        try:
            client = self.config_entry.runtime_data.client

            # Fetch the last trip (basic info first to get trip ID)
            trips = await client.async_get_trips(amount=1)
            last_trip = None
            if trips:
                # Get detailed trip info including geocoded locations
                last_trip = await client.async_get_trip_details(trips[0].tripId)

            # Get current date for badge and score queries
            today = datetime.now(tz=UTC).strftime("%Y-%m-%d")

            # Fetch daily badges (get today's badge - may not exist)
            daily_badges = await client.async_get_badges(
                badge_type="daily",
                start_date=today,
                end_date=today,
            )
            daily_badge = daily_badges[0] if daily_badges else None

            # Fetch monthly badges (get current month's badge - may not exist)
            first_of_month = datetime.now(tz=UTC).replace(day=1).strftime("%Y-%m-%d")
            monthly_badges = await client.async_get_badges(
                badge_type="monthly",
                start_date=first_of_month,
                end_date=today,
            )
            monthly_badge = monthly_badges[0] if monthly_badges else None

            return BonusdriveCoordinatorData(
                last_trip=last_trip,
                daily_badge=daily_badge,
                monthly_badge=monthly_badge,
            )
        except BonusdriveApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except BonusdriveApiClientError as exception:
            raise UpdateFailed(exception) from exception

"""API Client for Allianz BonusDrive."""

from __future__ import annotations

from typing import TYPE_CHECKING

from allianz_bonusdrive_client import (
    Badge,
    BonusdriveAPIClient,
    Scores,
    Trip,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class BonusdriveApiClientError(Exception):
    """Exception to indicate a general API error."""


class BonusdriveApiClientCommunicationError(BonusdriveApiClientError):
    """Exception to indicate a communication error."""


class BonusdriveApiClientAuthenticationError(BonusdriveApiClientError):
    """Exception to indicate an authentication error."""


class BonusdriveApiClient:
    """Async wrapper for the Allianz BonusDrive API Client."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        email: str,
        password: str,
        photon_url: str | None = None,
    ) -> None:
        """Initialize the API client."""
        self._hass = hass
        self._client = BonusdriveAPIClient(
            base_url=base_url,
            email=email,
            password=password,
            tgt=None,
            photon_url=photon_url,
        )
        self._authenticated = False

    async def async_authenticate(self) -> None:
        """Authenticate with the API."""
        try:
            await self._hass.async_add_executor_job(self._client.authenticate)
            self._authenticated = True
        except Exception as exception:
            msg = str(exception)
            if "401" in msg or "403" in msg or "auth" in msg.lower():
                raise BonusdriveApiClientAuthenticationError(msg) from exception
            raise BonusdriveApiClientCommunicationError(msg) from exception

    async def async_get_scores(
        self,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> dict[str, Scores] | list:
        """Get driving scores from the API."""
        if not self._authenticated:
            await self.async_authenticate()

        try:
            kwargs = {}
            if start_date:
                kwargs["startDate"] = start_date
            if end_date:
                kwargs["endDate"] = end_date

            result = await self._hass.async_add_executor_job(
                lambda: self._client.get_scores(**kwargs)
            )
        except ValueError:
            # JSON decode error - API returned empty response (no scores)
            return {}
        except Exception as exception:
            msg = f"Error fetching scores: {exception}"
            raise BonusdriveApiClientCommunicationError(msg) from exception
        else:
            return result if result else {}

    async def async_get_trips(
        self,
        amount: int = 10,
        offset: int = 0,
    ) -> list[Trip]:
        """Get trips from the API."""
        if not self._authenticated:
            await self.async_authenticate()

        try:
            return await self._hass.async_add_executor_job(
                lambda: self._client.get_trips(amount=amount, offset=offset)
            )
        except Exception as exception:
            msg = f"Error fetching trips: {exception}"
            raise BonusdriveApiClientCommunicationError(msg) from exception

    async def async_get_badges(
        self,
        badge_type: str = "daily",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[Badge]:
        """Get badges from the API."""
        if not self._authenticated:
            await self.async_authenticate()

        try:
            kwargs = {"type": badge_type}
            if start_date:
                kwargs["startDate"] = start_date
            if end_date:
                kwargs["endDate"] = end_date

            result = await self._hass.async_add_executor_job(
                lambda: self._client.get_badges(**kwargs)
            )
        except ValueError:
            # JSON decode error - API returned empty response (no badges)
            return []
        except Exception as exception:
            msg = f"Error fetching badges: {exception}"
            raise BonusdriveApiClientCommunicationError(msg) from exception
        else:
            return result if result else []

    async def async_get_vehicle_id(self) -> str:
        """Get the vehicle ID."""
        if not self._authenticated:
            await self.async_authenticate()

        try:
            return await self._hass.async_add_executor_job(self._client.get_vehicleId)
        except Exception as exception:
            msg = f"Error fetching vehicle ID: {exception}"
            raise BonusdriveApiClientCommunicationError(msg) from exception

    async def async_get_trip_details(self, trip_id: str) -> Trip:
        """Get detailed trip information including geocoded locations."""
        if not self._authenticated:
            await self.async_authenticate()

        try:
            return await self._hass.async_add_executor_job(
                lambda: self._client.get_trip_details(trip_id)
            )
        except Exception as exception:
            msg = f"Error fetching trip details: {exception}"
            raise BonusdriveApiClientCommunicationError(msg) from exception

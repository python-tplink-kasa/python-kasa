"""Implementation of vacuum."""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import TYPE_CHECKING

from ...feature import Feature
from ..smartmodule import SmartModule

if TYPE_CHECKING:
    from ..smartdevice import SmartDevice


_LOGGER = logging.getLogger(__name__)


class Status(IntEnum):
    """Status of vacuum."""

    Idle = 0
    Cleaning = 1
    GoingHome = 4
    Charging = 5
    Charged = 6
    Paused = 7
    Error = 100
    Unknown = 101


class Vacuum(SmartModule):
    """Implementation of vacuum support."""

    REQUIRED_COMPONENT = "clean"

    def __init__(self, device: SmartDevice, module: str) -> None:
        super().__init__(device, module)
        self._add_feature(
            Feature(
                device,
                id="vacuum_return_home",
                name="Return home",
                container=self,
                attribute_setter="return_home",
                category=Feature.Category.Primary,
                type=Feature.Action,
            )
        )
        self._add_feature(
            Feature(
                device,
                id="vacuum_start",
                name="Start cleaning",
                container=self,
                attribute_setter="start",
                category=Feature.Category.Primary,
                type=Feature.Action,
            )
        )
        self._add_feature(
            Feature(
                device,
                id="vacuum_pause",
                name="Pause",
                container=self,
                attribute_setter="pause",
                category=Feature.Category.Primary,
                type=Feature.Action,
            )
        )
        self._add_feature(
            Feature(
                device,
                id="vacuum_status",
                name="Vacuum status",
                container=self,
                attribute_getter="status",
                category=Feature.Category.Primary,
                type=Feature.Type.Sensor,
            )
        )
        self._add_feature(
            Feature(
                self._device,
                "battery_level",
                "Battery level",
                container=self,
                attribute_getter="battery",
                icon="mdi:battery",
                unit_getter=lambda: "%",
                category=Feature.Category.Info,
                type=Feature.Type.Sensor,
            )
        )

    def query(self) -> dict:
        """Query to execute during the update cycle."""
        return {"getVacStatus": None, "getBatteryInfo": None}

    async def start(self) -> dict:
        """Start cleaning."""
        # If we are paused, do not restart cleaning

        if self.status == Status.Paused:
            return await self.resume()

        # TODO: we need to create settings for clean_modes
        return await self.call(
            "setSwitchClean",
            {
                "clean_mode": 0,
                "clean_on": True,
                "clean_order": True,
                "force_clean": False,
            },
        )

    async def pause(self) -> dict:
        """Pause cleaning."""
        return await self.set_pause(True)

    async def resume(self) -> dict:
        """Resume cleaning."""
        return await self.set_pause(False)

    async def set_pause(self, enabled: bool) -> dict:
        """Pause or resume cleaning."""
        return await self.call("setRobotPause", {"pause": enabled})

    async def return_home(self) -> dict:
        """Return home."""
        return await self.set_return_home(True)

    async def set_return_home(self, enabled: bool) -> dict:
        """Return home / pause returning."""
        return await self.call("setSwitchCharge", {"switch_charge": enabled})

    @property
    def battery(self) -> int:
        """Return battery level."""
        return self.data["getBatteryInfo"]["battery_percentage"]

    @property
    def _vac_status(self) -> dict:
        """Return vac status container."""
        return self.data["getVacStatus"]

    @property
    def status(self) -> Status:
        """Return current status."""
        if self._vac_status.get("err_status"):
            return Status.Error

        status_code = self._vac_status["status"]
        try:
            return Status(status_code)
        except ValueError:
            _LOGGER.warning("Got unknown status code: %s (%s)", status_code, self.data)
            return Status.Unknown

"""Implementation of the motion detection (PIR) module found in some dimmers."""

from __future__ import annotations

import logging
from enum import Enum

from ...exceptions import KasaException
from ...feature import Feature
from ..iotmodule import IotModule

_LOGGER = logging.getLogger(__name__)


class Range(Enum):
    """Range for motion detection."""

    Far = 0
    Mid = 1
    Near = 2
    Custom = 3


# TODO: use the config reply in tests
# {"enable":0,"version":"1.0","trigger_index":2,"cold_time":60000,
# "min_adc":0,"max_adc":4095,"array":[80,50,20,0],"err_code":0}}}


class Motion(IotModule):
    """Implements the motion detection (PIR) module."""

    def _initialize_features(self):
        """Initialize features after the initial update."""
        # Only add features if the device supports the module
        if "get_config" not in self.data:
            return

        if "enable" not in self.data["get_config"]:
            _LOGGER.warning("%r initialized, but no get_config in response")
            return

        self._add_feature(
            Feature(
                device=self._device,
                container=self,
                id="pir_enabled",
                name="PIR enabled",
                icon="mdi:motion-sensor",
                attribute_getter="enabled",
                attribute_setter="set_enabled",
                type=Feature.Type.Switch,
                category=Feature.Category.Config,
            )
        )

    def query(self):
        """Request PIR configuration."""
        return self.query_for_command("get_config")

    @property
    def range(self) -> Range:
        """Return motion detection range."""
        return Range(self.data["get_config"]["trigger_index"])

    @property
    def enabled(self) -> bool:
        """Return True if module is enabled."""
        return bool(self.data["get_config"]["enable"])

    async def set_enabled(self, state: bool):
        """Enable/disable PIR."""
        return await self.call("set_enable", {"enable": int(state)})

    async def set_range(
        self, *, range: Range | None = None, custom_range: int | None = None
    ):
        """Set the range for the sensor.

        :param range: for using standard ranges
        :param custom_range: range in decimeters, overrides the range parameter
        """
        if custom_range is not None:
            payload = {"index": Range.Custom.value, "value": custom_range}
        elif range is not None:
            payload = {"index": range.value}
        else:
            raise KasaException("Either range or custom_range need to be defined")

        return await self.call("set_trigger_sens", payload)

    @property
    def inactivity_timeout(self) -> int:
        """Return inactivity timeout in milliseconds."""
        return self.data["get_config"]["cold_time"]

    async def set_inactivity_timeout(self, timeout: int):
        """Set inactivity timeout in milliseconds.

        Note, that you need to delete the default "Smart Control" rule in the app
        to avoid reverting this back to 60 seconds after a period of time.
        """
        return await self.call("set_cold_time", {"cold_time": timeout})

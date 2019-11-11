"""Python interface for TP-Link's smart home devices.

All common, shared functionalities are available through `SmartDevice` class::

    x = SmartDevice("192.168.1.1")
    print(x.sys_info)

For device type specific actions `SmartBulb`, `SmartPlug`, or `SmartStrip`
 should be used instead.

Module-specific errors are raised as `SmartDeviceException` and are expected
to be handled by the user of the library.
"""
from .discover import Discover  # noqa
from .protocol import TPLinkSmartHomeProtocol  # noqa
from .smartbulb import SmartBulb  # noqa
from .smartdevice import (  # noqa
    DeviceType,
    EmeterStatus,
    SmartDevice,
    SmartDeviceException,
)
from .smartplug import SmartPlug  # noqa
from .smartstrip import SmartStrip  # noqa
from .version import __version__  # noqa

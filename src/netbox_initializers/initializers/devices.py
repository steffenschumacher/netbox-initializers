from dcim.models import Device, DeviceRole, DeviceType, Location, Platform, Rack, Site
from tenancy.models import Tenant
from virtualization.models import Cluster

from .base import *
from . import register_initializer


class DeviceInitializer(BaseInitializer):
    def name(self):
        return "device"

    def icon(self):
        return "🖥"

    def nb_model(self):
        return Device

    def ignored_params(self) -> list[str]:
        return ["primary_ipv4", "primary_ipv6"]

    def data_file_name(self) -> str:
        return "devices.yml"

    def unique_params(self) -> list[str]:
        return ["device_type", "name", "site"]

    def required_associations(self) -> dict[str, (type, str)]:
        return {
            "device_role": (DeviceRole, "name"),
            "device_type": (DeviceType, "model"),
            "site": (Site, "name"),
        }

    def optional_associations(self) -> dict[str, (type, str)]:
        return {
            "tenant": (Tenant, "name"),
            "platform": (Platform, "name"),
            "rack": (Rack, "name"),
            "cluster": (Cluster, "name"),
            "location": (Location, "name"),
        }


register_initializer(DeviceInitializer)

from .base import BaseInitializer, InitializerConfig, SurvivableError, ImportNotNeeded
INITIALIZER_ORDER = (
    "users",
    "groups",
    "object_permissions",
    "custom_fields",
    "custom_links",
    "tags",
    "webhooks",
    "tenant_groups",
    "tenants",
    "regions",
    "sites",
    "locations",
    "rack_roles",
    "racks",
    "power_panels",
    "power_feeds",
    "manufacturers",
    "device_roles",
    "device_types",
    "devices",
    "interfaces",
    "platforms",
    "route_targets",
    "vrfs",
    "rirs",
    "asns",
    "aggregates",
    "prefix_vlan_roles",
    "cluster_types",
    "cluster_groups",
    "clusters",
    "vlan_groups",
    "vlans",
    "virtual_machines",
    "virtualization_interfaces",
    "prefixes",
    "ip_addresses",
    "primary_ips",
    "services",
    "providers",
    "circuit_types",
    "circuits",
    "cables",
    "contact_groups",
    "contact_roles",
    "contacts",
)

INITIALIZER_REGISTRY = dict()


def register_initializer(initializer: BaseInitializer):
    if InitializerConfig.is_updatable(initializer.nb_model.__name__):
        initializer.set_updates_allowed()
    INITIALIZER_REGISTRY[initializer.name] = initializer


# All initializers must be imported here, to be registered
from .aggregates import AggregateInitializer
from .asns import ASNInitializer
from .cables import CableInitializer
from .circuit_types import CircuitTypeInitializer
from .circuits import CircuitInitializer
from .cluster_groups import ClusterGroupInitializer
from .cluster_types import ClusterTypesInitializer
from .clusters import ClusterInitializer
from .contact_groups import ContactGroupInitializer
from .contact_roles import ContactRoleInitializer
from .contacts import ContactInitializer
from .custom_fields import CustomFieldInitializer
from .custom_links import CustomLinkInitializer
from .device_roles import DeviceRoleInitializer
from .device_types import DeviceTypeInitializer
from .devices import DeviceInitializer
from .groups import GroupInitializer
from .interfaces import InterfaceInitializer
from .ip_addresses import IPAddressInitializer
from .locations import LocationInitializer
from .manufacturers import ManufacturerInitializer
from .object_permissions import ObjectPermissionInitializer
from .platforms import PlatformInitializer
from .power_feeds import PowerFeedInitializer
from .power_panels import PowerPanelInitializer
from .prefix_vlan_roles import RoleInitializer
from .prefixes import PrefixInitializer
from .primary_ips import PrimaryIPInitializer
from .providers import ProviderInitializer
from .rack_roles import RackRoleInitializer
from .racks import RackInitializer
from .regions import RegionInitializer
from .rirs import RIRInitializer
from .route_targets import RouteTargetInitializer
from .services import ServiceInitializer
from .sites import SiteInitializer
from .tags import TagInitializer
from .tenant_groups import TenantGroupInitializer
from .tenants import TenantInitializer
from .users import UserInitializer
from .virtual_machines import VirtualMachineInitializer
from .virtualization_interfaces import VMInterfaceInitializer
from .vlan_groups import VLANGroupInitializer
from .vlans import VLANInitializer
from .vrfs import VRFInitializer
from .webhooks import WebhookInitializer

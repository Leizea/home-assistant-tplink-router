from dataclasses import dataclass
from collections.abc import Callable
from typing import Any
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import PERCENTAGE, UnitOfInformation
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from .const import DOMAIN
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .coordinator import TPLinkRouterCoordinator
from tplinkroutermr600 import Status


@dataclass
class TPLinkRouterSensorRequiredKeysMixin:
    value: Callable[[Status], Any]


@dataclass
class TPLinkRouterSensorEntityDescription(SensorEntityDescription, TPLinkRouterSensorRequiredKeysMixin):
    """A class that describes sensor entities."""


SENSOR_TYPES: tuple[TPLinkRouterSensorEntityDescription, ...] = (
    TPLinkRouterSensorEntityDescription(
        key="guest_wifi_clients_total",
        name="Total guest wifi clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda status: status.guest_clients_total,
    ),
    TPLinkRouterSensorEntityDescription(
        key="wifi_clients_total",
        name="Total main wifi clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda status: status.wifi_clients_total,
    ),
    TPLinkRouterSensorEntityDescription(
        key="wired_clients_total",
        name="Total wired clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda status: status.wired_total,
    ),
    TPLinkRouterSensorEntityDescription(
        key="iot_clients_total",
        name="Total IoT clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda status: status.iot_clients_total,
    ),
    TPLinkRouterSensorEntityDescription(
        key="clients_total",
        name="Total clients",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.TOTAL,
        value=lambda status: status.clients_total,
    ),
    TPLinkRouterSensorEntityDescription(
        key="cpu_used",
        name="CPU used",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        value=lambda status: (status.cpu_usage * 100) if status.cpu_usage is not None else None,
    ),
    TPLinkRouterSensorEntityDescription(
        key="memory_used",
        name="Memory used",
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=1,
        value=lambda status: (status.mem_usage * 100) if status.mem_usage is not None else None,
    ),
    TPLinkRouterSensorEntityDescription(
        key="wan_connection_type",
        name="WAN Connection type",
        icon="mdi:wan",
        value=lambda status: status.wan_connection_type,
    ),
    TPLinkRouterSensorEntityDescription(
        key="pppoe_connection_status",
        name="PPPoe connection status",
        icon="mdi:ethernet-cable",
        value=lambda status: status.pppoe_connection_status,
    ),
    TPLinkRouterSensorEntityDescription(
        key="lte_connection_status",
        name="LTE connection status",
        icon="mdi:signal-4g",
        value=lambda status: status.lte_connection_status,
    ),
    TPLinkRouterSensorEntityDescription(
        key="wan_ipv4_addr",
        name="WAN IP address",
        icon="mdi:ip-network",
        value=lambda status: status.wan_ipv4_addr,
    ), 
    TPLinkRouterSensorEntityDescription(
        key="wan_macaddr",
        name="WAN MAC address",
        icon="mdi:network-pos",
        value=lambda status: status.wan_macaddr,
    ),  
    TPLinkRouterSensorEntityDescription(
        key="wan_ipv4_gateway",
        name="WAN Gateway",
        icon="mdi:router-network",
        value=lambda status: status.wan_ipv4_gateway,
    ),
    TPLinkRouterSensorEntityDescription(
        key="wan_dns_servers",
        name="WAN DNS servers",
        icon="mdi:dns",
        value=lambda status: status.wan_dns_servers,
    ),                          
)


async def async_setup_entry(
        hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    for description in SENSOR_TYPES:
        sensors.append(TPLinkRouterSensor(coordinator, description))
    async_add_entities(sensors, False)


class TPLinkRouterSensor(
    CoordinatorEntity[TPLinkRouterCoordinator], SensorEntity
):
    _attr_has_entity_name = True
    entity_description: TPLinkRouterSensorEntityDescription

    def __init__(
            self,
            coordinator: TPLinkRouterCoordinator,
            description: TPLinkRouterSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)

        self._attr_device_info = coordinator.device_info
        self._attr_unique_id = f"{coordinator.unique_id}_{DOMAIN}_{description.key}"
        self.entity_description = description

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.entity_description.value(self.coordinator.status)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.entity_description.value(self.coordinator.status) is not None

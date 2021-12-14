"""Device handler for PTVO Meteostation Ver 1"""
from zigpy.profiles import zha
from zigpy.quirks import CustomCluster, CustomDevice
from zhaquirks import Bus, LocalDataCluster
from zigpy.zcl.clusters.homeautomation import Diagnostic
from zigpy.zcl.clusters.general import Basic, BinaryInput, OnOff, AnalogInput, MultistateInput, GreenPowerProxy
from zigpy.zcl.clusters.measurement import TemperatureMeasurement, RelativeHumidity, PressureMeasurement


from zhaquirks.const import (
    DEVICE_TYPE,
    ENDPOINTS,
    INPUT_CLUSTERS,
    MODELS_INFO,
    OUTPUT_CLUSTERS,
    PROFILE_ID,
)

DEV_TEMPERATURE_REPORTED = "dev_temperature_reported"
TEMPERATURE_REPORTED = "temperature_reported"
HUMIDITY_REPORTED = "humidity_reported"
PRESSURE_REPORTED = "pressure_reported"

PTVO_DEVICE = 0xfffe
GREEN_POWER_DEVICE = 0x0061
GP_DEVICE_ID = 0xA1E0


class PtvoAnalogInputCluster(CustomCluster, AnalogInput):
    """Analog input cluster, used to relay temperature, humidity and Pressure to Meteostation cluster."""

    cluster_id = AnalogInput.cluster_id

    def __init__(self, *args, **kwargs):
        """Init."""
        self._current_state = {}
        self._current_value = 0
        super().__init__(*args, **kwargs)

    def _update_attribute(self, attrid, value):
        super()._update_attribute(attrid, value)
        
        if value is not None:
        
            if attrid == 85:
                self._current_value = value
            
            if attrid == 28:
                if value == "C":
                    """Device temperature value."""
                    d_value = self._current_value * 100
                    self.endpoint.device.dev_temperature_bus.listener_event(DEV_TEMPERATURE_REPORTED, d_value)
                
                if value == "C,44":
                    """Temperature value."""
                    t_value = self._current_value * 100
                    self.endpoint.device.temperature_bus.listener_event(TEMPERATURE_REPORTED, t_value)
                
                if value == "%,44":
                    """Humidity value."""
                    h_value = self._current_value * 100
                    self.endpoint.device.humidity_bus.listener_event(HUMIDITY_REPORTED, h_value)
                
                if value == "Pa,76":
                    """Pressure value."""
                    p_value = int(self._current_value) / 100
                    self.endpoint.device.pressure_bus.listener_event(PRESSURE_REPORTED, p_value)


class DevTemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.dev_temperature_bus.add_listener(self)

    def dev_temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class TemperatureMeasurementCluster(LocalDataCluster, TemperatureMeasurement):

    cluster_id = TemperatureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.temperature_bus.add_listener(self)

    def temperature_reported(self, value):
        """Temperature reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class HumidityMeasurementCluster(LocalDataCluster, RelativeHumidity):
    """Humidity measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = RelativeHumidity.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.humidity_bus.add_listener(self)

    def humidity_reported(self, value):
        """Humidity reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class PressureMeasurementCluster(LocalDataCluster, PressureMeasurement):
    """Pressure measurement cluster to receive reports that are sent to the analog cluster."""

    cluster_id = PressureMeasurement.cluster_id
    MEASURED_VALUE_ID = 0x0000

    def __init__(self, *args, **kwargs):
        """Init."""
        super().__init__(*args, **kwargs)
        self.endpoint.device.pressure_bus.add_listener(self)

    def pressure_reported(self, value):
        """Humidity reported."""
        self._update_attribute(self.MEASURED_VALUE_ID, value)


class meteostation(CustomDevice):
    """Meteostation Ver 1 based on PTVO firmware."""

    def __init__(self, *args, **kwargs):
        """Init device."""
        self.dev_temperature_bus = Bus()
        self.temperature_bus = Bus()
        self.humidity_bus = Bus()
        self.pressure_bus = Bus()
        
        super().__init__(*args, **kwargs)

    signature = {
        MODELS_INFO: [("ptvo.info", "meteostation")],
        ENDPOINTS: {
            # <SimpleDescriptor endpoint=1 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[0, 12]
            # output_clusters=[0, 18]>
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    AnalogInput.cluster_id,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    MultistateInput.cluster_id,
                ],
            },
            # <SimpleDescriptor endpoint=2 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[6]
            # output_clusters=[6]>
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [OnOff.cluster_id],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            # <SimpleDescriptor endpoint=3 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[6]
            # output_clusters=[6]>
            3: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [OnOff.cluster_id],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            # <SimpleDescriptor endpoint=4 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[12]
            # output_clusters=[]>
            4: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },

            # <SimpleDescriptor endpoint=5 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[12]
            # output_clusters=[]>
            5: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },
            # <SimpleDescriptor endpoint=7 profile=260 device_type=65534
            # device_version=1
            # input_clusters=[12]
            # output_clusters=[]>
            7: {
                PROFILE_ID: zha.PROFILE_ID,
                DEVICE_TYPE: PTVO_DEVICE,
                INPUT_CLUSTERS: [AnalogInput.cluster_id],
                OUTPUT_CLUSTERS: [],
            },
            # <SimpleDescriptor endpoint=242 profile=41440 device_type=65534
            # device_version=1
            # input_clusters=[12]
            # output_clusters=[]>
            242: {
                PROFILE_ID: GP_DEVICE_ID,
                DEVICE_TYPE: GREEN_POWER_DEVICE,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
            
        },
    }

    replacement = {
        ENDPOINTS: {
            1: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [
                    Basic.cluster_id,
                    AnalogInput.cluster_id,
                    TemperatureMeasurementCluster,
                    HumidityMeasurementCluster,
                    PressureMeasurementCluster,
                ],
                OUTPUT_CLUSTERS: [
                    Basic.cluster_id,
                    MultistateInput.cluster_id,
                ],
            },
            2: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [
                    DevTemperatureMeasurementCluster,
                ],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            3: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [OnOff.cluster_id],
            },
            4: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [PtvoAnalogInputCluster],
                OUTPUT_CLUSTERS: [],
            },
            5: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [PtvoAnalogInputCluster],
                OUTPUT_CLUSTERS: [],
            },
            7: {
                PROFILE_ID: zha.PROFILE_ID,
                INPUT_CLUSTERS: [PtvoAnalogInputCluster],
                OUTPUT_CLUSTERS: [],
            },
            242: {
                INPUT_CLUSTERS: [],
                OUTPUT_CLUSTERS: [GreenPowerProxy.cluster_id],
            },
        },
    }
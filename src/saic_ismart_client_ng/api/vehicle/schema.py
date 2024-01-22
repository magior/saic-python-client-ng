import base64
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from saic_ismart_client_ng.api.schema import GpsPosition

LOGGER = logging.getLogger(__name__)


@dataclass
class VehicleModelConfiguration:
    itemCode: str = None
    itemName: str = None
    itemValue: str = None


@dataclass
class SubAccount:
    authorizationCardType: int = None
    btKeyStatus: int = None
    locationAuthorization: int = None
    modelName: str = None
    operationType: int = None
    status: int = None
    subaccountId: int = None
    subscriberId: int = None
    userAccount: str = None
    userName: str = None
    validityEndTime: int = None
    validityStartTime: int = None
    vin: str = None


@dataclass
class VinInfo:
    bindTime: int = None
    brandName: str = None
    colorName: str = None
    isActivate: bool = None
    isCurrentVehicle: bool = None
    isSubaccount: bool = None
    modelName: str = None
    modelYear: str = None
    name: str = None
    series: str = None
    vin: str = None
    subAccountList: List[SubAccount] = field(default_factory=list)
    vehicleModelConfiguration: List[VehicleModelConfiguration] = field(default_factory=list)


@dataclass
class VehicleListResp:
    vinList: List[VinInfo] = field(default_factory=list)


@dataclass
class BasicVehicleStatus:
    batteryVoltage: int = None
    bonnetStatus: int = None
    bootStatus: int = None
    canBusActive: int = None
    clstrDspdFuelLvlSgmt: int = None
    currentJourneyID: int = None
    currentjourneyDistance: int = None
    dippedBeamStatus: int = None
    driverDoor: int = None
    driverWindow: int = None
    engineStatus: int = None
    extendedData1: int = None
    extendedData2: int = None
    exteriorTemperature: int = None
    frontLeftSeatHeatLevel: int = None
    frontLeftTyrePressure: int = None
    frontRightSeatHeatLevel: int = None
    frontRightTyrePressure: int = None
    fuelLevelPrc: int = None
    fuelRange: int = None
    fuelRangeElec: int = None
    handbrake: int = None
    interiorTemperature: int = None
    lastKeySeen: int = None
    lockStatus: int = None
    mainBeamStatus: int = None
    mileage: int = None
    passengerDoor: int = None
    passengerWindow: int = None
    powerMode: int = None
    rearLeftDoor: int = None
    rearLeftTyrePressure: int = None
    rearLeftWindow: int = None
    rearRightDoor: int = None
    rearRightTyrePressure: int = None
    rearRightWindow: int = None
    remoteClimateStatus: int = None
    rmtHtdRrWndSt: int = None
    sideLightStatus: int = None
    sunroofStatus: int = None
    timeOfLastCANBUSActivity: int = None
    vehElecRngDsp: int = None
    vehicleAlarmStatus: int = None
    wheelTyreMonitorStatus: int = None


@dataclass
class ExtendedVehicleStatus:
    alertDataSum: list = field(default_factory=list)


@dataclass
class VehicleStatusResp:
    basicVehicleStatus: BasicVehicleStatus = None
    extendedVehicleStatus: ExtendedVehicleStatus = None
    gpsPosition: GpsPosition = None
    statusTime: int = None

    @property
    def is_charging(self) -> bool:
        return (
                self.basicVehicleStatus and
                self.basicVehicleStatus.extendedData2
                and self.basicVehicleStatus.extendedData2 >= 1
        )

    @property
    def is_parked(self) -> bool:
        return (
                self.basicVehicleStatus.engineStatus != 1
                or self.basicVehicleStatus.handbrake
        )

    @property
    def is_engine_running(self) -> bool:
        return self.basicVehicleStatus.engineStatus == 1


class RvcParamsId(Enum):
    FIND_MY_CAR_ENABLE = 1
    FIND_MY_CAR_HORN = 2
    FIND_MY_CAR_LIGHTS = 3
    UNK_4 = 4
    UNK_5 = 5
    UNK_6 = 6
    LOCK_ID = 7
    WINDOW_SUNROOF = 8
    WINDOW_DRIVER = 9
    WINDOW_2 = 10
    WINDOW_3 = 11
    WINDOW_4 = 12
    WINDOW_OPEN_CLOSE = 13
    HEATED_SEAT_DRIVER = 17
    HEATED_SEAT_PASSENGER = 18
    FAN_SPEED = 19
    TEMPERATURE = 20
    AC_ON_OFF = 22
    REMOTE_HEAT_REAR_WINDOW = 23
    PARAMS_MAX = 0xFF


@dataclass
class RvcParams:
    paramId: int
    paramValue: str

    def __init__(self, param_id: RvcParamsId, param_value: bytes):
        self.paramId = param_id.value
        self.paramValue = base64.b64encode(param_value).decode('utf-8')


class RvcReqType(Enum):
    FIND_MY_CAR = "0"
    CLOSE_LOCKS = "1"
    OPEN_LOCKS = "2"
    WINDOWS = "3"
    KEY_MANAGEMENT = "4"
    HEATED_SEATS = "5"
    CLIMATE = "6"
    AIR_CLEAN = "7"
    ENGINE_CONTROL = "17"
    REMOTE_REFRESH = "18"
    REMOTE_IMMOBILIZER = "19"
    REMOTE_HEAT_REAR_WINDOW = "32"
    MAX_VALUE = "597"


@dataclass
class VehicleControlReq:
    rvcParams: List[RvcParams]
    rvcReqType: str
    vin: str

    def __init__(self, rvc_params: List[RvcParams], rvc_req_type: RvcReqType, vin: str):
        self.rvcParams = rvc_params
        self.rvcReqType = rvc_req_type.value
        self.vin = vin

    @property
    def rvc_req_type_decoded(self) -> Optional[bytes]:
        try:
            if self.rvcReqType:
                return base64.b64decode(self.rvcReqType)
        except Exception as e:
            LOGGER.error("Failed to decode rvcReqType: %s", self.rvcReqType, exc_info=e)
        return None


@dataclass
class VehicleControlResp:
    basicVehicleStatus: BasicVehicleStatus = None
    failureType: int = None
    gpsPosition: GpsPosition = None
    rvcReqSts: str = None
    rvcReqType: str = None

    @property
    def rvc_req_sts_decoded(self) -> Optional[bytes]:
        try:
            if self.rvcReqSts:
                return base64.b64decode(self.rvcReqSts)
        except Exception as e:
            LOGGER.error("Failed to decode rvcReqSts: %s", self.rvcReqSts, exc_info=e)
        return None

    @property
    def rvc_req_type_decoded(self) -> Optional[bytes]:
        try:
            if self.rvcReqType:
                return base64.b64decode(self.rvcReqType)
        except Exception as e:
            LOGGER.error("Failed to decode rvcReqType: %s", self.rvcReqType, exc_info=e)
        return None

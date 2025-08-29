from pydantic import BaseModel, Field
from typing import Optional, List


class TokenOut(BaseModel):
 access_token: str
 token_type: str = "bearer"


class LoginIn(BaseModel):
 username: str
 password: str


class SiteIn(BaseModel):
 code: str
 name: str


class SiteOut(SiteIn):
 id: str

class FloorplanIn(BaseModel):
 site_id: str
 name: str
 page_index: int = 0


class FloorplanOut(FloorplanIn):
 id: str
 file_url: str
 width_px: int | None = None
 height_px: int | None = None


class DeviceIn(BaseModel):
 site_id: str
 device_id: str
 display_name: str
 model: str | None = None
 manufacturer: str | None = None

class DeviceOut(DeviceIn):
 id: str


class SensorIn(BaseModel):
 device_id: str
 sensor_key: str
 display_name: str
 icon: str
 unit_ui: str


class SensorOut(SensorIn):
 id: str


class PlacementIn(BaseModel):
 floorplan_id: str
 sensor_id: str
 x_rel: float
 y_rel: float
 rotation_deg: float | None = None

class PlacementOut(PlacementIn):
 id: str


class ThresholdIn(BaseModel):
 sensor_id: str
 strategy: str # 'abs_range' | 'moving_mean_std'
 min_value: float | None = None
 max_value: float | None = None
 window_n: int | None = None
 k_std: float | None = None
 severity: str = "major"
 enabled: bool = True


class ThresholdOut(ThresholdIn):
 id: str

class TimeseriesQuery(BaseModel):
 device_id: str
 metric: str
 t_from: str
 t_to: str


class TimeseriesPoint(BaseModel):
 t: str
 v: float


class LatestValueOut(BaseModel):
 sensor_uuid: str
 display_name: str
 icon: str
 unit_ui: str
 value: float | None
 time: str | None

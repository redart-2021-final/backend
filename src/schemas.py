import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class UserSchemaMe(BaseModel):
    id: UUID  # noqa: VNE003 A003
    username: str

    class Config:
        orm_mode = True


class UserSchemaCreate(BaseModel):
    username: str
    password: str


class UserSchemaChild(BaseModel):
    id: UUID  # noqa: VNE003 A003
    username: str
    color: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery: Optional[float] = None
    accuracy: Optional[float] = None

    class Config:
        orm_mode = True


class DeviceSchemaOwn(BaseModel):
    id: UUID  # noqa: VNE003 A003
    name: str
    extra: dict

    class Config:
        orm_mode = True


class DeviceSchemaInUpdate(BaseModel):
    name: str
    extra: dict


class DeviceSchemaIn(BaseModel):
    name: str
    extra: Optional[dict] = None
    child_id: UUID


class EventSchema(BaseModel):
    timestamp: datetime.datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    extra: Optional[dict] = None

    class Config:
        orm_mode = True


class EventSchemaInItem(BaseModel):
    timestamp: datetime.datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    battery: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    extra: Optional[dict] = None


class EventSchemaIn(BaseModel):
    events: list[EventSchemaInItem]
    device_id: Optional[UUID] = None


class Point(BaseModel):
    latitude: float
    longitude: float

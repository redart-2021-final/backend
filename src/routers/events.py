from typing import Union
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Response,
)

from models import Event, User
from routers.deps import auth, get_user_device
from schemas import EventSchema, EventSchemaIn

router = APIRouter(
    prefix='/events',
    tags=['events'],
)


@router.get('', response_model=list[EventSchema])
async def list_(device_id: UUID, user: User = Depends(auth)) -> Union[list[EventSchema], Response]:
    device = await user.devices.filter(id=device_id).first()
    if not device:
        return Response(status_code=404)
    qs = await device.events.all()
    serialized = [EventSchema.from_orm(device) for device in qs]
    return serialized


@router.post('', status_code=201, response_class=Response)
async def create(
        user: User = Depends(auth),
        event_data: EventSchemaIn = Body(...),
) -> Response:
    device = await get_user_device(user, event_data.device_id)
    if not device:
        return Response(status_code=404)
    events = [Event(**event.dict(exclude_none=True), device=device) for event in event_data.events]
    await Event.bulk_create(events)
    return Response(status_code=201)

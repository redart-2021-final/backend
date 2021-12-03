from datetime import datetime
from typing import Union, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    Response,
)
from sklearn import linear_model

from models import User
from routers.deps import auth, get_user_device
from schemas import Point

router = APIRouter(
    prefix='/predict',
    tags=['predict'],
)


@router.get('', response_model=Point)
async def predict(
        user: User = Depends(auth),
        device_id: Optional[UUID] = None,
        child_id: Optional[UUID] = None,
) -> Union[Point, Response]:
    child = await user.children.filter(id=child_id).first()
    if not child:
        return Response(status_code=404)
    device = await get_user_device(child, device_id)
    if not device:
        return Response(status_code=404)

    def time_to_array(timestamp: datetime) -> list:
        return [timestamp.day, timestamp.hour, timestamp.minute]

    events = await device.events.all().order_by('-timestamp').limit(10)
    times = [time_to_array(event.timestamp) for event in events]
    locations = [[event.latitude, event.longitude] for event in events]
    model = linear_model.LinearRegression()
    model.fit(times, locations)
    latitude, longitude = model.predict([time_to_array(datetime.utcnow())])[0]
    serialized = Point(latitude=latitude, longitude=longitude)
    return serialized

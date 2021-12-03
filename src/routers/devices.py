from typing import Optional, Union
from uuid import UUID

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Path,
    Response,
)

from models import Device, User
from routers.deps import auth
from schemas import (
    DeviceSchemaIn,
    DeviceSchemaInUpdate,
    DeviceSchemaOwn,
)

router = APIRouter(
    prefix='/devices',
    tags=['devices'],
)


@router.get('', response_model=list[DeviceSchemaOwn])
async def list_(
        user: User = Depends(auth),
        child_id: Optional[UUID] = None,
) -> Union[list[DeviceSchemaOwn], Response]:
    if child_id:
        child = await user.children.filter(id=child_id).first()
        if not child:
            return Response(status_code=404)
        qs = await child.devices.all()
    else:
        qs = await user.devices.all()
    serialized = [DeviceSchemaOwn.from_orm(device) for device in qs]
    return serialized


@router.post('', response_model=DeviceSchemaOwn)
async def create(
        user: User = Depends(auth),
        device_data: DeviceSchemaIn = Body(...),
) -> Union[DeviceSchemaOwn, Response]:
    if device_data.child_id:
        child = await user.children.filter(id=device_data.child_id).first()
        if not child:
            return Response(status_code=404)
        owner = child
        device_data.child_id = None
    else:
        owner = user
    device = await Device.create(**device_data.dict(exclude_none=True), owner=owner)
    serialized = DeviceSchemaOwn.from_orm(device)
    return serialized


@router.patch('/{device_id}', response_model=DeviceSchemaOwn)
async def update(
        user: User = Depends(auth),
        device_data: DeviceSchemaInUpdate = Body(...),
        device_id: UUID = Path(...),
) -> DeviceSchemaOwn:
    device = await user.devices.filter(pk=device_id).get()
    await device.update_from_dict(device_data.dict(exclude_none=True)).save()
    serialized = DeviceSchemaOwn.from_orm(device)
    return serialized


@router.delete('/{device_id}', status_code=204)
async def delete_(user: User = Depends(auth), device_id: UUID = Path(...)) -> Response:
    device = await user.devices.filter(pk=device_id).get()
    await device.delete()
    return Response(status_code=204)

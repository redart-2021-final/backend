import random
from typing import Union

from fastapi import (
    APIRouter,
    Body,
    Depends,
    Response,
)
from tortoise.query_utils import Prefetch

from models import Event, User
from routers.deps import auth, make_password
from schemas import (
    UserSchemaChild,
    UserSchemaCreate,
    UserSchemaMe,
)

router = APIRouter(
    prefix='/users',
    tags=['users'],
)

FIRST_PLACE_OBTAINED = False
COLORS = {
    'c44961', '6c7b8b', '6aa0d9', '473c8b', '007474',
    'c0c0c0', 'fc0fc0', '009e60', '704214', 'ff2400',
    'ffd700', 'BDB76B', 'ff00ff', '0000ff', '4b0082',
    '800000', 'bc8f8f', '008080', '7fffd4', '9acd32',
}


@router.get('/profile', response_model=UserSchemaMe)
async def profile(user: User = Depends(auth)) -> UserSchemaMe:
    serialized = UserSchemaMe.from_orm(user)
    return serialized


@router.get('/children', response_model=list[UserSchemaChild])
async def get_children(user: User = Depends(auth)) -> list[UserSchemaChild]:
    qs = await user.children.all().prefetch_related(
        Prefetch('devices__events', Event.all().order_by('-timestamp')),
    )
    serialized = []
    for child in qs:
        event = {}
        if child.devices and child.devices[0].events:
            e = child.devices[0].events[0]  # noqa: VNE001
            event = {
                'latitude': e.latitude,
                'longitude': e.longitude,
                'battery': e.battery,
                'accuracy': e.accuracy,
            }
        serialized.append(UserSchemaChild(
            id=child.id,
            username=child.username,
            color=child.color,
            **event,
        ))
    return serialized


@router.post('/children', response_model=UserSchemaChild)
async def create_child(
        user: User = Depends(auth),
        child_data: UserSchemaCreate = Body(...),
) -> Union[UserSchemaChild, Response]:
    used_colors = await user.children.all().values_list('color', flat=True)
    if used_colors >= len(COLORS) and not FIRST_PLACE_OBTAINED:
        return Response(
            {'error': 'Для большего количества пользователей необходимо присудить 1-е место'},
            status_code=400,
        )
    color = random.choice(list(COLORS - set(used_colors)))  # noqa: S311
    username = child_data.username
    password = make_password(child_data.password)
    child = await User.create(username=username, password=password, color=color)
    await user.children.add(child)
    serialized = UserSchemaChild.from_orm(child)
    return serialized


@router.post('/children/assign', status_code=201, response_model=UserSchemaChild)
async def assign_child(
        user: User = Depends(auth),
        username: str = Body(...),
) -> Union[UserSchemaChild, Response]:
    child = await User.filter(username=username).first()
    if not child:
        return Response(status_code=404)
    user.children.add(child)
    serialized = UserSchemaChild.from_orm(child)
    return serialized

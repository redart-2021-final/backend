import base64
import hashlib
import secrets
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from tortoise.exceptions import DoesNotExist

from models import User, Device

security = HTTPBasic()


async def auth(credentials: HTTPBasicCredentials = Depends(security)) -> User:
    try:
        user = await User.get(username=credentials.username)
    except DoesNotExist:
        raise HTTPException(status_code=401)
    if not check_password(credentials.password, user.password):
        raise HTTPException(status_code=401)
    return user


def make_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 666_666
    alg = 'sha256'
    hashed = hashlib.pbkdf2_hmac(alg, password.encode(), salt.encode(), iterations)
    hashed = base64.b64encode(hashed).decode().strip()
    return '$'.join([alg, str(iterations), salt, hashed])


def check_password(password: str, encoded: str) -> bool:
    alg, iterations, salt, hashed = encoded.split('$')
    iterations = int(iterations)
    new_hashed = hashlib.pbkdf2_hmac(alg, password.encode(), salt.encode(), iterations)
    new_hashed = base64.b64encode(new_hashed).decode().strip()
    return secrets.compare_digest(hashed, new_hashed)


async def get_user_device(user: User, device_id: Optional[UUID] = None) -> Optional[Device]:
    if device_id:
        return await user.devices.filter(id=device_id).first()

    devices = await user.devices.all().count()
    if not devices:
        return await Device.create(owner=user, name='auto')
    elif devices == 1:
        return await user.devices.all().first()

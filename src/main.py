#!/bin/env python3

import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

import config
from routers import (
    devices,
    events,
    predict,
    users,
)

app = FastAPI(
    title='ReDart',
    debug=config.DEBUG,
)

app.include_router(users.router, prefix='/api')
app.include_router(devices.router, prefix='/api')
app.include_router(events.router, prefix='/api')
app.include_router(predict.router, prefix='/api')

register_tortoise(app, config=config.ORM)


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.LISTEN,
        port=config.PORT,
        loop='uvloop',
    )

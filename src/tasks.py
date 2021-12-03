#!/bin/env python3

import asyncio
import datetime

import httpx
import pandas as pd
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from scipy.stats import mstats
from tortoise import Tortoise

import config
from models import Event

redis = Redis.from_url(config.BROKER)
queue = Queue(connection=redis)
scheduler = Scheduler(queue=queue, connection=redis)

repeated_jobs = {
    'tasks.process_events': {
        'args': [],
        'kwargs': {},
        'interval': 60,
    }
}


class KalmanFilter:
    """
    https://pbs.twimg.com/media/EEkW3ZmUEAAa8Be.jpg
    """

    def __init__(self):
        self.mean_deviation = 0.00023
        self.process = 0.05
        self.Pc = 0.0
        self.G = 0.0
        self.P = 1.0
        self.Xp = 0.0
        self.Zp = 0.0
        self.Xe = 0.0

    def _single_filter(self, value):
        self.Pc = self.P + self.process
        self.G = self.Pc / (self.Pc + self.mean_deviation)
        self.P = (1 - self.G) * self.Pc
        self.Xp = self.Xe
        self.Zp = self.Xp
        self.Xe = self.G * (value - self.Zp) + self.Xp
        return self.Xe

    def filter(self, data: list) -> list:
        result = [self._single_filter(i) for i in data]
        return result


def init_jobs() -> None:
    now = datetime.datetime.utcnow()
    current_jobs = scheduler.get_jobs()
    jobs_by_func = {job.func_name: job for job in current_jobs}
    for rjob_name, rjob_data in repeated_jobs.items():
        job = jobs_by_func.get(rjob_name)
        if not job:
            scheduler.schedule(now, rjob_name, **rjob_data)
            print(f'scheduled job {rjob_name}')
            continue
        if job.meta['interval'] != rjob_data['interval']:
            job.meta['interval'] = rjob_data['interval']
            job.save()
            print(f'updated job {rjob_name}')


async def _process_event(client: httpx.AsyncClient, event: Event) -> None:
    print(f'start update event {dict(event)}')

    params = {
        'lat': event.latitude,
        'lon': event.longitude,
        'format': 'jsonv2',
    }
    try:
        response = await client.get(config.NOMINATIM + '/reverse', params=params)
    except Exception as e:
        print(f'error update event {event.id} {e}')
        return

    event.extra['geo'] = response.json()
    event.processed = True
    await event.save()

    print(f'finished update event {event.id}')


async def _process_events() -> None:
    await Tortoise.init(config.ORM)
    tasks = []
    qs = await Event.filter(processed=False).limit(20)
    print(f'fetched {len(qs)}')

    async with httpx.AsyncClient() as client:
        for event in qs:
            tasks.append(_process_event(client, event))
        await asyncio.gather(*tasks, return_exceptions=True)

    def quantile_filter(data: list):
        return pd.Series(mstats.winsorize(data, limits=[0.05, 0.05])).tolist()

    latitude = [event.latitude for event in qs]
    longitude = [event.longitude for event in qs]
    filter_latitude = KalmanFilter()
    filter_longitude = KalmanFilter()
    filtered_latitude = filter_latitude.filter(quantile_filter(latitude))
    filtered_longitude = filter_longitude.filter(quantile_filter(longitude))

    for latitude, longitude, event in zip(filtered_latitude, filtered_longitude, qs):
        event.latitude = latitude
        event.longitude = longitude

    await Tortoise.close_connections()


def process_events() -> None:
    asyncio.run(_process_events())


if __name__ == '__main__':
    init_jobs()

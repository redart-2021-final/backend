#!/bin/env python3

import asyncio
import datetime

import httpx
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
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
    await Tortoise.close_connections()


def process_events() -> None:
    asyncio.run(_process_events())


if __name__ == '__main__':
    init_jobs()

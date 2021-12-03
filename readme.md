## Основной стек технологий

- python 3.9, fastapi, scikit-learn
- docker, docker-compose
- postgresql, redis

**Демо API:** http://2021.jlemyp.xyz/docs  
Тестовый юзер - tim 123

## Установка и запуск

### минимальные требования

- database (postgres рекомендуется)
- queue broker - redis
- python 3.9+
- git, gcc, make, libc-dev

или docker и docker-compose

### a) установка с docker

установить docker и docker-compose

миграция бд:
```shell
docker-compose -f docker/compose.yml run --rm worker upgrade
```

### b) установка без docker

установить python 3.9+, pip, git, gcc, make, libc-dev. названия пакетов для debian/ubuntu.

1) создать бд и пользователя
2) запустить redis
3) установить poetry: `pip insatll poetry`
4) миграция бд:
```shell
poetry install --no-dev
DB_URL=<...> poetry run aerich upgrade
```

### Настройки

*должны быть переданы в переменных окружения*

- DEBUG (true) - bool
- *DB_URL - url
- *BROKER_URL - url

'*' - обязательные

### a) запуск с docker

```shell
docker-compose -f docker/compose.yml up -d backend
```

запуск гео базы урала (долго инициализируется и много места жрет) и фоновых процессов обновления точек:
```shell
docker-compose -f docker/compose.yml up -d geobase worker scheduler dashboard
```

### b) запуск без docker

```shell
poetry shell
export DB_URL=<...>
cd src
rq worker &
rqscheduler &
./main.py
```

---

**авторы**:

- Тимофей (backend) - https://t.me/jlemyp
- Тимофей (frontend, lead) - https://t.me/tsuvorkov
- Ирина (дизайнер) - https://t.me/irinzv
- Борис (оратор, аналитик) - https://t.me/gelborious
- Александр (аналитик, ml разработчик) - https://t.me/Salexandr18

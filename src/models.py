from tortoise import fields, models


class UuidPkMixin(models.Model):
    id = fields.UUIDField(pk=True)  # noqa: VNE003 A003

    class Meta:
        abstract = True


class User(UuidPkMixin):
    username = fields.CharField(max_length=256, unique=True)
    password = fields.CharField(max_length=256)
    children = fields.ManyToManyField('core.User', related_name='parents')
    color = fields.CharField(max_length=6, null=True)

    devices: fields.ReverseRelation['Device']
    parents: fields.ReverseRelation['User']

    def __str__(self) -> str:
        return self.username


class Device(UuidPkMixin):
    owner = fields.ForeignKeyField('core.User', related_name='devices')
    name = fields.CharField(max_length=256)
    extra = fields.JSONField(default=dict)
    deleted = fields.BooleanField(default=False)

    events: fields.ReverseRelation['Event']

    def __str__(self) -> str:
        return self.name


class Event(UuidPkMixin):
    device = fields.ForeignKeyField('core.Device', related_name='events')
    timestamp = fields.DatetimeField(auto_now_add=True)
    latitude = fields.FloatField(null=True)
    longitude = fields.FloatField(null=True)
    battery = fields.FloatField(null=True)
    accuracy = fields.FloatField(null=True)
    speed = fields.FloatField(null=True)
    extra = fields.JSONField(default=dict)
    processed = fields.BooleanField(default=False)


__models__ = [User, Device, Event]

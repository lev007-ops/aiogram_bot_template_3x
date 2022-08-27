import peewee as pw

from tgbot.config import load_config

config = load_config().db

db = pw.PostgresqlDatabase(config.database,
                           user=config.user,
                           password=config.password,
                           host=config.host,
                           port=config.port
                           autorollback=True)


class BaseModel(pw.Model):
    id = pw.PrimaryKeyField()

    class Meta:
        database = db

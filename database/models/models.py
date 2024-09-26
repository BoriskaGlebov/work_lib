import functools
from datetime import datetime
import peewee
from playhouse.sqlite_ext import *

db = peewee.SqliteDatabase('disk_sercher.db')
# Для отключения экранирования в таблицах
my_json_dumps = functools.partial(json.dumps, ensure_ascii=False)


class ModelBase(peewee.Model):
    """Модель базы данных"""
    created_at = peewee.DateTimeField(default=datetime.now().
                                      strftime('%Y-%m-%d %X'))

    class Meta:
        database = db


class Hosts(ModelBase):
    """Таблица с информацией о хостах"""
    created_at = peewee.DateTimeField(default=datetime.now().
                                      strftime('%Y-%m-%d %X'))
    updated_at = peewee.DateTimeField(default=datetime.now().
                                      strftime('%Y-%m-%d %X'))
    host_name = peewee.TextField(null=False)
    name_os = peewee.TextField(null=False)

    # class Meta:
    #     database = db
    # table_name = 'her' #можно переопределить название таблицы


class DiskInfo(ModelBase):
    """Таблица с информацией о дисках"""
    created_at = peewee.DateTimeField(default=datetime.now().strftime('%Y-%m-%d %X'))
    updated_at = peewee.DateTimeField(default=datetime.now().
                                      strftime('%Y-%m-%d %X'))
    # host = peewee.ForeignKeyField(Hosts, backref='query')
    host = peewee.TextField(primary_key=True)
    manufactured_id = peewee.TextField()
    model_name = peewee.TextField()
    total_size = peewee.TextField()
    int_size = peewee.IntegerField()
    serial_number = peewee.TextField()

    def to_json(self):
        return {field:getattr(self,field) for field in self._meta.columns}
    # class Meta:
    #     database = db


db.connect()
db.create_tables([Hosts, DiskInfo])

if __name__ == '__main__':
    pass

from typing import TypeVar, List, Dict
from peewee import SqliteDatabase
from database.models.models import *

T = TypeVar('T')


class CRUInterface:
    """
    Создание, чтение, обновление, удаление данных их БД
    """

    @classmethod
    def insert_single_host(cls, host_name: str, name_os: str, model: T = Hosts) -> None:
        """
        Метод добавляет хост в БД.
        Если такой хост уже есть, то обновляется информация о нем в БД
        :param host_name: hostname
        :param name_os: название ОС
        :param model: название таблицы, для добавления
        :return: добвляется запись в таблицу
        """
        sel = model.select().where(model.host_name == host_name)
        # Проверка, есть ли такой хост БД
        if sel.__len__():
            # если такой хост есть в БД, то обновляю информацию
            # о нем, при необходимости будет заменено название ОС, если вдруг на хосте
            # она поменялась
            # так же будет записано последнее время обновления информацции
            print('Произошло обновление данных хоста')
            cr_time = datetime.now().strftime('%Y-%m-%d %X')
            for el in sel:
                el.name_os = name_os
                el.updated_at = cr_time
            with db.atomic():
                Hosts.bulk_update(sel, fields=['updated_at', 'host_name', 'name_os'])
        else:
            # Если такого хоста нет в БД, то данные добавляются в БД
            model.create(host_name=host_name, name_os=name_os)
            print(f'Добавил {host_name}')
        return None

    @classmethod
    def insert_disk_data(cls, data: List[Dict], model_disk: T = DiskInfo, model_host: T = Hosts) -> None:
        """
        Добавление информации о дисках хоста
        Если данный об этом хосте уже есть, то происходит обновление информации.
        :param data: list[dict] Данные по жестким дискам
        :param model_disk: таблица дисков
        :param model_host: таблица хостов
        :return: добавляется или удаляется или обновляется запись о дисках
        """
        sel = model_disk.select().join(model_host).where(model_host.host_name == data[0]['host'].host_name)
        cr_time = datetime.now().strftime('%Y-%m-%d %X')
        if len(sel) == 0:
            # Если такогго хоста не было, то добавляется информация
            model_disk.insert_many(data).execute()
            print('Данные добавлены в таблицу')
        elif len(sel) == len(data):
            # Если такой хост уже есть в БД и у него дисков
            # столько же сколько я хочу добавить, то ионформация обновляется
            print('Произошло обновление данных дисков хоста')
            for num, el in enumerate(sel):
                el.updated_at = cr_time
                el.manufactured_id = data[num]['manufactured_id']
                el.model_name = data[num]['model_name']
                el.total_size = data[num]['total_size']
                el.serial_number = data[num]['serial_number']
            with db.atomic():
                DiskInfo.bulk_update(sel, fields=['updated_at', 'manufactured_id', 'model_name', 'total_size',
                                                  'serial_number'])
        elif len(sel) < len(data):
            # Если такой хост уже есть в БД и у него дисков меньше
            # чем я хочу добавить, то информация обновляется и добавляется
            for num, el in enumerate(sel):
                el.updated_at = cr_time
                el.manufactured_id = data[num]['manufactured_id']
                el.model_name = data[num]['model_name']
                el.total_size = data[num]['total_size']
                el.serial_number = data[num]['serial_number']
            with db.atomic():
                DiskInfo.bulk_update(sel, fields=['updated_at', 'manufactured_id', 'model_name', 'total_size',
                                                  'serial_number'])
            model_disk.insert_many(data[len(sel):]).execute()
        else:
            # Если такой хост уже есть в БД и у него дисков больше
            # чем я хочу добавить, то информация обновляется и удаляется лишнее
            for num, el in enumerate(sel):
                if num >= len(data):
                    el.delete_instance()
                    continue
                el.updated_at = cr_time
                el.manufactured_id = data[num]['manufactured_id']
                el.model_name = data[num]['model_name']
                el.total_size = data[num]['total_size']
                el.serial_number = data[num]['serial_number']

            with db.atomic():
                DiskInfo.bulk_update(sel, fields=['updated_at', 'manufactured_id', 'model_name', 'total_size',
                                                  'serial_number'])

    @classmethod
    def delete_host(cls, hostname: str) -> None:
        """
        Удаляется хост, а так же диски которые ему принадлежали
        из обеих таблиц, если такой хост не найдет, то вернется None
        :param hostname: hostname
        :return: None
        """
        res = Hosts.get_or_none(Hosts.host_name == hostname)  # ищу удаляемый хост
        if res:
            # удаляю хост
            res.delete_instance(recursive=True)

    @classmethod
    def retrive_host_disk(cls, host_name) -> list[dict]:
        """
        Возарвщаю список с информацией о дисках конкретного хоста
        :param host_name: hod=stname
        :return: список словарей [{'host_name': 'host1',
            'manufactured_id': 'Seagete', 'model_name': '123QWER',
            'serial_number': 'ASD0987IOP', 'total_size': '480 Gb'},.....]
        """
        res = DiskInfo.select(Hosts.host_name, DiskInfo.manufactured_id, DiskInfo.model_name,
                              DiskInfo.serial_number, DiskInfo.total_size).join(Hosts).where(
            Hosts.host_name == host_name).dicts()
        return list(res)


if __name__ == '__main__':
    # Сначало получаем словарь {host:system} и надо такие данные добавить в БД
    host1 = CRUInterface.insert_single_host('host1', 'windows')
    host2 = CRUInterface.insert_single_host('host2', 'linux')
    host3 = CRUInterface.insert_single_host('host3', 'bsd')
    host4 = CRUInterface.insert_single_host('host4', 'vmware')
    host5 = CRUInterface.insert_single_host('host5', 'windows')

    # все таки в списке с утсройствами нужно добавить название
    # хоста и так пожно добавлять диски хоста в другую таблицу разом
    disk_data1 = [{'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987IOP'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987SDF'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987POI'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987YTR'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987WER'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagete',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987RYT'},
                  {'host': Hosts.get(host_name='host1'),
                   'manufactured_id': 'Seagetes',
                   'model_name': '123QWER',
                   'total_size': '480 Gb',
                   'serial_number': 'ASD0987RYT'}
                  ]
    disk_data2 = [{'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'QWE987IOP'},
                  {'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'RTY0987SDF'},
                  {'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'UIO0987POI'},
                  {'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'ASD0987YTR'},
                  {'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'FGH0987WER'},
                  {'host': Hosts.get(host_name='host2'),
                   'manufactured_id': 'HP_RECOVERY_GROUP',
                   'model_name': 'QWER987POI',
                   'total_size': '987 Gb',
                   'serial_number': 'JKL0987RYT'}
                  ]
    disk_data3 = [{'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'QWE987IOP'},
                  {'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'RTY0987SDF'},
                  {'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'UIO0987POI'},
                  {'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'ASD0987YTR'},
                  {'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'FGH0987WER'},
                  {'host': Hosts.get(host_name='host3'),
                   'manufactured_id': 'MSI',
                   'model_name': 'ERY8375WEPRO',
                   'total_size': '2 TB',
                   'serial_number': 'JKL0987RYT'}
                  ]

    CRUInterface.insert_disk_data(data=disk_data1)
    CRUInterface.insert_disk_data(data=disk_data2)
    CRUInterface.insert_disk_data(data=disk_data3)
    # for el in disk_data3:
    #     el['host'] = Hosts.get(Hosts.host_name == 'host1')
    # print(disk_data3)
    # CRUInterface.insert_disk_data(data=disk_data3)
    # # CRUDinterace.delete_host('host1')
    # # CRUDinterace.delete_host('host2')
    # # CRUDinterace.delete_host('host3')
    # # CRUDinterace.delete_host('host4')
    # # CRUDinterace.delete_host('host5')
    #
    # res = list(CRUInterface.retrive_host_disk('host1'))
    # print(res[0])

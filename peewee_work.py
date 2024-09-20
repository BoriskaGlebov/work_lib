from database.models.models import db, DiskInfo

if __name__ == '__main__':
    db.drop_tables(DiskInfo)
    db.create_tables([DiskInfo,])
    d = {'host': 'test_host',
         'manufactured_id': 'asdfghhjkl0qrwt',
         'model_name': 'Hitachy',
         'total_size': '123Gb',
         'int_size': 123,
         'serial_number': 'dsf2325fsf'
         }
    disk_list = [{k: (v if k != 'host' else v + str(i))
                  for k, v in d.items()}
                 for i in range(40000)]
    # print(disk_list)
    ins_inf=[DiskInfo(**el) for el in disk_list]
    print(len(ins_inf))
    with db.atomic():
        DiskInfo.bulk_create(ins_inf)
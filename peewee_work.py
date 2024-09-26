import time

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
                 for i in range(100000)]
    # print(disk_list)
    ins_inf=[DiskInfo(**el) for el in disk_list]
    print(len(ins_inf))
    strat=time.time()
    # ds=DiskInfo.create()
    # print(type(ds))
    # for el in disk_list:
    for el in range(0,len(disk_list),10000):
        DiskInfo.insert_many(disk_list[el:el+10000]).execute()
    # with db.atomic():
    #     DiskInfo.bulk_create(ins_inf,batch_size=30000)
        # DiskInfo.bulk_create(ins_inf)
    print(f'work for {time.time()-strat=}')
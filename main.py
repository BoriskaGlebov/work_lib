import string
import random
import time

import Levenshtein


def replace(replace_str: str):
    """
    Функция заменяет возможные опечатки на моменте сравнения,
    строка после проверки останется без изменений
    :param replace_str: строка которую нужно сравнить
    :return: измененная строка
    """
    replace_str = replace_str.replace('O', '0')
    replace_str = replace_str.replace('G', '6')
    return replace_str


letters = string.ascii_uppercase + string.digits
# print(letters)
serial_numbers = []
# генерирую диски db
with open('from_db.txt', 'w') as file:
    while len(serial_numbers) < 1000:
        some_num = ''
        for _ in range(10):
            some_num += random.choice(letters)
        serial_numbers.append(some_num)
        file.write(some_num + '\n')
# генерирую ошибочные в exel
# рандомно делает опечатки 'O' и '0', 'G' и '6'
# рандомно заменяет один рандомный символ на любой другой, создает эффект отличия серийника на один символ
with open('from_exel.txt', 'w') as file:
    for serial_num in serial_numbers:
        new_str = serial_num
        # добавляю опечатки
        if random.randint(1, 100) == 1:
            new_str = serial_num.replace('O', '0')
            new_str = new_str.replace('G', '6')
        # добавляю другие символы, так сказать различие на один символ
        if random.randint(1, 6) == 1:
            new_str = new_str.replace(serial_num[random.randint(0, len(new_str) - 1)], random.choice(letters))
        file.write(new_str + '\n')

# вот после подготовительных мероприятий приступаю собственно к сравнению
print('я создаль')
start = time.time()
with open('from_db.txt', 'r') as file1, open('from_exel.txt', 'r') as file2:
    from_db = file1.readlines()
    from_exel = file2.readlines()
    # в этот список кладу все отличающиеся серийники из БД
    out = []
    for hdd in from_db:
        for hdd_exel in from_exel:
            if hdd == hdd_exel or Levenshtein.distance(hdd, hdd_exel, processor=replace) == 0:
                # Сюда можно дописать, что делать если диски одинаковые,
                # например поместить в какой-то словарь, где будут данные из БД и EXEL
                # для вставки в таблицу на сайте.
                # Так же если данные из exel это тоже список,
                # то я бы удалял из него все что находим,
                # тем самым думаю немного будет ускоряться поиск
                from_exel.remove(hdd_exel)
                break
            else:
                continue
        else:
            out.append(hdd)
    stop= time.time()
    print(len(out))
    print(out)
    print(f'time = {stop-start}')

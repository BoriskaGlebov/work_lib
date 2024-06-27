import string
import random
import Levenshtein


def replace(replace_str: str):
    replace_str = replace_str.replace('O', '0')
    replace_str = replace_str.replace('G', '6')
    return replace_str


letters = string.ascii_uppercase + string.digits
# print(letters)
serial_numbers = []
# генерирую диски db
# with open('from_db.txt', 'w') as file:
#     while len(serial_numbers) < 20:
#         some_num = ''
#         for _ in range(10):
#             some_num += random.choice(letters)
#         serial_numbers.append(some_num)
#         file.write(some_num + '\n')
# print(serial_numbers)
# генерирую ошибочные в exel
# with open('from_exel.txt', 'w') as file:
#     for serial_num in serial_numbers:
#         new_str = serial_num
#         if random.randint(1, 3) == 1:
#             new_str = serial_num.replace('O', '0')
#             new_str = new_str.replace('G', '6')
#         file.write(new_str + '\n')
# смотрю сколько в итоге не совпадает
with open('from_db.txt', 'r') as file1, open('from_exel.txt', 'r') as file2:
    from_db = file1.readlines()
    from_exel = file2.readlines()
    out = []
    for num1, num2 in zip(from_db, from_exel):
        if num1 != num2:
            # print(num1.strip(), num2)
            out.append((num1, num2))
        # else:
        # print(num1.strip(), num2)
    # print(len(out))

    for from_db, from_exel in out:
        if Levenshtein.distance(from_db,from_exel,processor=replace):
            print(from_db,from_exel)
        else:
            print(from_db,from_exel)
        # print(Levenshtein.distance(from_db, from_exel, processor=replace))
# a = 'BNMOBYN34GX'
# c = 'BNM0BYN34X6'
# d = 'BNMOBYN34M'
# print(Levenshtein.distance(a, c, processor=replace))
# # print(Levenshtein.distance(a, d, weights=(1, 1, 2)))
# #
# # print(Levenshtein.jaro_winkler(a, d, prefix_weight=0.25))
# print((Levenshtein.ratio(a, c,processor=replace)))
# # print((Levenshtein.ratio(a,d)))
# print(replace(a))

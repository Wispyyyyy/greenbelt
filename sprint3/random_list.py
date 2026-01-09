import random

def randList(size, bottom, top):
    rand_list = []
    for i in range(size):
        rand_list.append(random.randint(bottom, top))
    return rand_list

small_list = randList(10, 1, 20)
medium_list = randList(50,0,100)
large_list = (100,0,100)

print("SMALL LIST: {}" .format(small_list))
print("MEDIUM LIST: {}" .format(medium_list))
print(f"LARGE LIST: {large_list}" )

import random

def randList(size, bottom, top):
    rand_list = []
    for i in range(size):
        rand_list.append(random.randint(bottom, top))
    return rand_list


medium_list = randList(50,0,100)

list = [50, 100, 10, 80, 1000]

for i in range (0, len(list)):
    min_index = i
    for j in range (i+1, len(list)):
        if list[min_index] > list[j]:
            min_index = j
    list[min_index], list[i] = list[i], list[min_index]
print(list)
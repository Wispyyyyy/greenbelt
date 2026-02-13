import random
import time

def randList(size, bottom, top):
    rand_list = []
    for i in range(size):
        rand_list.append(random.randint(bottom, top))
    return rand_list

def timeStamp():
    return time.time()



list = randList(10000 ,0,100)


def selection_sort():
    for i in range (0, len(list)):
        min_index = i
        for j in range (i+1, len(list)):
            if list[min_index] > list[j]:
                min_index = j
        list[min_index], list[i] = list[i], list[min_index]
    


def bubble_sort():
    for i in range (0, len(list)):
        for j in range (0, len(list) - 1):
            if list[j] < list[j+1]:
                list[j], list[j+1] = list[j+1], list[j]
                
def binary_search():
    target = random.choice(list)
    index = len(list) - 1

    end = index 
    start = 0
    middle = list[(start + end)//2]


    while start <= end:
        middle = (start+end)//2
        if list[middle] == target:
            target_index = middle
            print(f"Your target number is at index: {target_index}. Your target was {target}!")
            break

        elif list[middle] > target:
            start = 0
            end = middle - 1
            
        elif list[middle] < target:
            start = middle + 1
            end = len(list)
            



SS_time_start = timeStamp()
selection_sort()
SS_time_end = timeStamp()

BUS_time_start = timeStamp()
bubble_sort()
BUS_time_end = timeStamp()

BS_time_start = timeStamp()
binary_search()
BS_time_end = timeStamp()


print(f"The time for Selection sort was {SS_time_end - SS_time_start} seconds.")

print(f"The time for Bubble sort was {BUS_time_end - BUS_time_start} seconds.")

print(f"The time for Binary search was {BS_time_end - BS_time_start} seconds.")




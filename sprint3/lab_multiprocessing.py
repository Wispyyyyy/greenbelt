import cProfile
import multiprocessing
import random
import time





sorted_list = []

def bubble_sort(arr):
    for j in range (len(arr) - 1):
        for i in range(0, len(arr) - j - 1):
            if arr[i] > arr[i+1]:
                arr[i], arr[i+1] = arr[i+1], arr[i]
    return arr

def selection_sort(arr):
    for i in range(len(arr) - 1):
        min_index = i - 1
        for j in range(i+1, len(arr)):
            if arr[min_index] > arr[j]:
                min_index = j
            # else:
            #     continue
        arr[min_index], arr[i] = arr[i], arr[min_index]
        # arr[len(arr) - 2], arr[0] = arr[0], arr[len(arr) - 2]
        return arr
    


def somefunction(arr):
    pr = cProfile.Profile()
    pr.enable()
    bubble_sort(arr.copy())
    pr.disable()
    pr.print_stats()


def somefunction2(arr):
    pr = cProfile.Profile()
    pr.enable()
    selection_sort(arr.copy())
    pr.disable()
    pr.print_stats()




if __name__ == "__main__":
    arr = [random.randint(0, 1000) for x in range(1000)]
    # sorted_list = bubble_sort(arr)
    # print(sorted_list == sorted(arr))

    # sorted_list2 = selection_sort(arr)
    # print(sorted_list2 == sorted(arr))
    # print(sorted_list2)

    p1 = multiprocessing.Process(target=somefunction, args=(arr, ))
    p2 = multiprocessing.Process(target=somefunction2, args=(arr, ))

    start_time = time.time()

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    end_time = time.time()


    print(f"Total elapsed time: {end_time - start_time} seconds.")



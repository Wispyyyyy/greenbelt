

list = [1, 5, 9, 11, 14, 19, 39, 51, 67, 80]
# target_found = False
target = 14
index = len(list) - 1

end = index 
start = 0
middle = list[(start + end)//2]


while start <= end:
    middle = (start+end)//2
    print(middle)
    if list[middle] == target:
        target_index = middle
        print(f"Your target number is at index: {target_index}. Your target was {target}!")
        print(list)
        break
    elif list[middle] > target:
        start = 0
        end = middle
        print(list)
    elif list[middle] < target:
        start = middle
        end = len(list)
        print(list)

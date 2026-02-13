list = [67, 4, 9, 10000, 453]

for i in range (0, len(list)):
    for j in range (0, len(list) - 1):
        if list[j] < list[j+1]:
            list[j], list[j+1] = list[j+1], list[j]
print(list)




# merge sort
def merge(arr, l, m, r):
    numOfLeftElements = m - l + 1
    numOfRightElements = r - m
#comment
    leftArray = [0] * numOfLeftElements
    rightArray = [0] * numOfRightElements


    for i in range(numOfLeftElements):
        leftArray[i] = arr[l + i]

    for j in range(numOfRightElements):
        rightArray[j] = arr[m+1+j]


    i = 0
    j = 0
    k = l


    while i < numOfLeftElements and j < numOfRightElements:
        if leftArray[i] <= rightArray[j]:
            arr[k] = leftArray[i]
            i+=1
        else:
            arr[k] = rightArray[j]
            j+=1
        k+=1
    while i < numOfLeftElements:
        arr[k] = leftArray[i]
        i+=1
        k+=1

    while j < numOfRightElements:
        arr[k] = rightArray[j]
        j+=1
        k+=1

def mergeSort(arr, l, r):
    if l < r:
        m = l + (r - l) // 2

        mergeSort(arr, l, m)
        mergeSort(arr, m+1, r)

        merge(arr, l, m, r)



arr = [100, 24, 16, 19, 54, 2, 191, 191, 1, -5, 500, 987, 0]

n = len(arr)

print("Given array is")
for i in range(n):
    print("%d" % arr[i], end = " ")

mergeSort(arr, 0, n - 1)

print("\n\nSorted array is ")
for i in range(n):
    print("%d" % arr[i], end = " ")


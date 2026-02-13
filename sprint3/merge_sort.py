list = [100, 24, 16, 19, 54, 2, 191, 191, 1, -5, 500, 987, 0]

length = len(list - 1)
# merge sort
def merge(arr, l, m, r):
    n1 = m - l + 1
    n2 = r - m
#comment
    L = [0] * (n1)
    R = [0] * (n2)


    for i in range(0, n1):
        L[i] = arr[l + i]

    for j in range(0, n2):
        R[j] = arr[m+1+i]


    i = 0
    j = 0
    k = l






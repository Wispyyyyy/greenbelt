num = int(input("Pick a number."))



def fibonacci_sequence(num):


    a = 0
    b = 1

    print(a)
    print(b)

    for i in range (2, num):

        c = a+b
        a=b
        b=c
        print(c)

fibonacci_sequence(num)
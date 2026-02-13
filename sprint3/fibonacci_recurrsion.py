n = int(input("Choose a number."))



def fibonacci(n):
    if n <=1:
        return n
    else:
        # print(fibonacci(n))
        return fibonacci(n - 1) + fibonacci(n-2)
        
if n<=0:
    print(f"{n} is not a valid number.")
else:
    for i in range(n):
        print(fibonacci(i))
    
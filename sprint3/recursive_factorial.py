var = 0
n = int(input("Choose a number."))

def recursive_factorial(n):
    if n == 1:
        return n
    elif n <= 0:
        print("Undefined.")
    else:
        var =  n * recursive_factorial(n-1)
        print(var)
        return var
       
recursive_factorial(n)

# 1*1 = , 2*1 = 2, 
    
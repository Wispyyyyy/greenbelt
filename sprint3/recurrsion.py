num = int(input("Choose a number."))


def recursive_factorial(num):
    if num < 0:
        print(f"{num} is an invalid input.")
    elif num == 0:
        print("Factorial of 0 is one.")
    elif num == 1:
        return num
    else:
        return num * recursive_factorial(num - 1)
        

print(recursive_factorial(num))


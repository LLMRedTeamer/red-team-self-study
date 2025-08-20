def divisionTest(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return "ERROR: Division by Zero"
    except Exception as e:
        return f"Error: {e}"


first = int(input("First number? "))
second = int(input("Second number? "))

print(divisionTest(first, second))


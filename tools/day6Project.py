def divideInHalf(x):
    try:
        return float(x) / 2
    except Exception:
        return None

inputs = [i for i in input("Enter values separated by spaces: ").split()]
results = [divideInHalf(x) for x in inputs if divideInHalf(x) is not None]

with open("testResults.txt", "w") as f:
    for r in results:
        f.write(str(r) + "\n")

with open("testResults.txt", "r") as f:
    for line in f:
        print(line.strip())
        

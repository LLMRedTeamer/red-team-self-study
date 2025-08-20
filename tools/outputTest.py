lines = ["Red teaming LLMs", "is fun and addictive", "but also serious and important"]

with open("outputTest.txt", "w") as f:
    for line in lines:
        f.write(line + "\n")

with open ("outputTest.txt", "r") as f:
    for line in f:
        print(line.strip())

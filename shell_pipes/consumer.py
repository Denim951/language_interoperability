numbers = []

for line in __import__("sys").stdin:
    numbers.append(float(line))

total = sum(numbers)

print("Numbers:", numbers)
print("Sum:", total)
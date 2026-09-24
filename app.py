print("House Expense Tracker")

item = input("What did you buy? ")
amount = float(input("How much did it cost? "))

with open("expenses.csv", "a") as file:
    file.write(item + "," + str(amount) + "\n")

print("Saved:", item, "-", amount)

total = 0
with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        total = total + float(parts[1])

print("Total spent so far:", total)


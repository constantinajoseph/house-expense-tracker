from datetime import date

print("House Expense Tracker")

item = input("What did you buy? ")
item = item.replace(",", " ")
category = input("Category (groceries/utilities/other): ")
amount = float(input("How much did it cost? "))
today = date.today()

with open("expenses.csv", "a") as file:
    file.write(str(today) + "," + item + "," + category + "," + str(amount) + "\n")

print("Saved:", item, "-", amount)

total = 0
with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 4:
            total = total + float(parts[3])

print("Total spent so far:", total)
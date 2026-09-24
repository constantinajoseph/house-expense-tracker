from datetime import date

this_month = str(date.today())[:7]

total = 0
by_category = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 4:
            day = parts[0]
            category = parts[2]
            amount = float(parts[3])
            if day[:7] == this_month:
                total = total + amount
                if category in by_category:
                    by_category[category] = by_category[category] + amount
                else:
                    by_category[category] = amount

print("Summary for", this_month)
print("Total:", total)
for category in by_category:
    print(category, "-", by_category[category])
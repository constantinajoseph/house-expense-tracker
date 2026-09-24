totals_by_month = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 4:
            month = parts[0][:7]
            amount = float(parts[3])
            if month in totals_by_month:
                totals_by_month[month] = totals_by_month[month] + amount
            else:
                totals_by_month[month] = amount

previous = None
for month in sorted(totals_by_month):
    total = totals_by_month[month]
    print(month, "-", total)
    if previous is not None:
        change = total - previous
        if change > 0:
            print("   Up by", change)
        elif change < 0:
            print("   Down by", -change)
        else:
            print("   Same as last month")
    previous = total
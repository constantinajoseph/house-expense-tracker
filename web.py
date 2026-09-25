import streamlit as st
from datetime import date
import pandas as pd
import os

st.title("House Expense Tracker")

if not os.path.exists("expenses.csv"):
    with open("expenses.csv", "w") as file:
        pass

item = st.text_input("What did you buy?")
category = st.selectbox("Category", ["groceries", "utilities", "other"])
amount = st.number_input("How much did it cost?", min_value=0.0)

if st.button("Save expense"):
    item = item.replace(",", " ")
    today = date.today()
    with open("expenses.csv", "a") as file:
        file.write(str(today) + "," + item + "," + category + "," + str(amount) + "\n")
    st.success("Saved: " + item + " - " + str(amount))

st.divider()
st.subheader("This Month's Summary")

this_month = str(date.today())[:7]
total = 0
by_category = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 4:
            day = parts[0]
            row_category = parts[2]
            amount_value = float(parts[3])
            if day[:7] == this_month:
                total = total + amount_value
                if row_category in by_category:
                    by_category[row_category] = by_category[row_category] + amount_value
                else:
                    by_category[row_category] = amount_value

st.write("Total spent:", total)
for row_category in by_category:
    st.write(row_category, "-", by_category[row_category])

st.divider()
st.subheader("All Expenses")

try:
    data = pd.read_csv("expenses.csv", header=None, names=["Date", "Item", "Category", "Amount"])
    data = data.sort_values("Date", ascending=False)
    st.dataframe(data, width="stretch")
except pd.errors.EmptyDataError:
    st.write("No expenses yet.")

st.divider()
st.subheader("Month-to-Month Comparison")

totals_by_month = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 4:
            month = parts[0][:7]
            amount_value = float(parts[3])
            if month in totals_by_month:
                totals_by_month[month] = totals_by_month[month] + amount_value
            else:
                totals_by_month[month] = amount_value

previous = None
for month in sorted(totals_by_month):
    month_total = totals_by_month[month]
    if previous is not None:
        change = month_total - previous
        if change > 0:
            st.write(month, "-", month_total, "(Up by", change, ")")
        elif change < 0:
            st.write(month, "-", month_total, "(Down by", -change, ")")
        else:
            st.write(month, "-", month_total, "(Same as last month)")
    else:
        st.write(month, "-", month_total)
    previous = month_totals
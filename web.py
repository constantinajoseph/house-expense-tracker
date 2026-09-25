import streamlit as st
from datetime import date

st.title("House Expense Tracker")

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
            category = parts[2]
            amount_value = float(parts[3])
            if day[:7] == this_month:
                total = total + amount_value
                if category in by_category:
                    by_category[category] = by_category[category] + amount_value
                else:
                    by_category[category] = amount_value

st.write("Total spent:", total)
for category in by_category:
    st.write(category, "-", by_category[category])
    st.divider()
st.subheader("All Expenses")

import pandas as pd

try:
    data = pd.read_csv("expenses.csv", header=None, names=["Date", "Item", "Category", "Amount"])
    data = data.sort_values("Date", ascending=False)
    st.dataframe(data, use_container_width=True)
except FileNotFoundError:
    st.write("No expenses yet.")
import streamlit as st
from datetime import date
import pandas as pd
import os
import time

st.title("House Expense Tracker")

if not os.path.exists("expenses.csv"):
    with open("expenses.csv", "w") as file:
        pass

if "house_code" not in st.session_state:
    st.session_state.house_code = ""

house_code = st.text_input("Enter your house code (share this with your housemates)", value=st.session_state.house_code)
st.session_state.house_code = house_code

if not house_code:
    st.info("Please enter a house code above to continue. Use the same code as your housemates to share expenses.")
    st.stop()

with st.form("expense_form", clear_on_submit=True):
    item = st.text_input("What did you buy?")
    category = st.selectbox("Category", ["groceries", "utilities", "other"], index=None, placeholder="Select category")
    amount = st.number_input("How much did it cost?", min_value=0.0, value=None, placeholder="Enter the amount")
    submitted = st.form_submit_button("Save expense")

if submitted:
    if item and category and amount:
        item = item.replace(",", " ")
        today = date.today()
        with open("expenses.csv", "a") as file:
            file.write(house_code + "," + str(today) + "," + item + "," + category + "," + str(amount) + "\n")
        message = st.empty()
        message.success("Saved: " + item + " - " + str(amount))
        time.sleep(2)
        message.empty()
    else:
        st.warning("Please fill in all fields before saving.")

st.divider()
st.subheader("This Month's Summary")

this_month = str(date.today())[:7]
total = 0
by_category = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 5 and parts[0] == house_code:
            day = parts[1]
            row_category = parts[3]
            amount_value = float(parts[4])
            if day[:7] == this_month:
                total = total + amount_value
                if row_category in by_category:
                    by_category[row_category] = by_category[row_category] + amount_value
                else:
                    by_category[row_category] = amount_value

st.write("Total spent:", total)
for row_category in by_category:
    st.markdown(f":blue[{row_category}] - **{by_category[row_category]}**")

st.divider()
st.subheader("All Expenses")

try:
    data = pd.read_csv("expenses.csv", header=None, names=["House", "Date", "Item", "Category", "Amount"])
    data = data[data["House"] == house_code]
    data = data.drop(columns=["House"])
    data = data.sort_values("Date", ascending=False)
    data.insert(0, "S.No", range(1, len(data) + 1))
    st.dataframe(data, width="stretch", hide_index=True)
except pd.errors.EmptyDataError:
    st.write("No expenses yet.")

st.divider()
st.subheader("Delete an Expense")

try:
    all_data = pd.read_csv("expenses.csv", header=None, names=["House", "Date", "Item", "Category", "Amount"])
    delete_data = all_data[all_data["House"] == house_code].reset_index(drop=True)
    if len(delete_data) == 0:
        st.write("No expenses to delete.")
    else:
        options = []
        for i in range(len(delete_data)):
            row = delete_data.iloc[i]
            label = str(row["Date"]) + " - " + str(row["Item"]) + " - " + str(row["Category"]) + " - " + str(row["Amount"])
            options.append(label)

        choice = st.selectbox("Pick an expense to delete", options)

        if st.button("Delete this expense"):
            index_to_delete = options.index(choice)
            row_to_remove = delete_data.iloc[index_to_delete]
            match = (
                (all_data["House"] == row_to_remove["House"]) &
                (all_data["Date"] == row_to_remove["Date"]) &
                (all_data["Item"] == row_to_remove["Item"]) &
                (all_data["Category"] == row_to_remove["Category"]) &
                (all_data["Amount"] == row_to_remove["Amount"])
            )
            first_match_index = all_data[match].index[0]
            all_data = all_data.drop(first_match_index)
            all_data.to_csv("expenses.csv", header=False, index=False)
            st.success("Deleted: " + choice)
            st.rerun()
except pd.errors.EmptyDataError:
    st.write("No expenses to delete.")

st.divider()
st.subheader("Month-to-Month Comparison")

totals_by_month = {}

with open("expenses.csv", "r") as file:
    for line in file:
        parts = line.strip().split(",")
        if len(parts) == 5 and parts[0] == house_code:
            month = parts[1][:7]
            amount_value = float(parts[4])
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
    previous = month_total
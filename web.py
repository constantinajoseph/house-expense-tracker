import streamlit as st
from datetime import date
import pandas as pd
import os
import time
import hashlib

st.title("House Expense Tracker")

if not os.path.exists("expenses.csv"):
    with open("expenses.csv", "w") as file:
        pass

if not os.path.exists("users.csv"):
    with open("users.csv", "w") as file:
        pass

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    users = {}
    with open("users.csv", "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 2:
                users[parts[0]] = {"password": parts[1]}
    return users

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.subheader("Login or Create an Account")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in"):
            users = load_users()
            if login_username in users and users[login_username]["password"] == hash_password(login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    with tab2:
        new_username = st.text_input("Choose a username", key="new_username")
        new_password = st.text_input("Choose a password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")

        if st.button("Sign up"):
            users = load_users()
            if not new_username or not new_password:
                st.warning("Please fill in all fields.")
            elif new_username in users:
                st.error("That username is already taken.")
            elif new_password != confirm_password:
                st.error("Passwords don't match.")
            else:
                with open("users.csv", "a") as file:
                    file.write(new_username + "," + hash_password(new_password) + "\n")
                # Log the new user straight in instead of leaving them on this tab
                st.session_state.logged_in = True
                st.session_state.username = new_username
                st.success("Account created!")
                time.sleep(1)
                st.rerun()

    st.stop()

st.write("Logged in as: **" + st.session_state.username + "**")
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

username = st.session_state.username

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
            file.write(username + "," + str(today) + "," + item + "," + category + "," + str(amount) + "\n")
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
        if len(parts) == 5:
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
    data = pd.read_csv("expenses.csv", header=None, names=["Added By", "Date", "Item", "Category", "Amount"])
    data = data.sort_values("Date", ascending=False)
    data.insert(0, "S.No", range(1, len(data) + 1))
    st.dataframe(data, width="stretch", hide_index=True)
except pd.errors.EmptyDataError:
    st.write("No expenses yet.")

st.divider()
st.subheader("Delete an Expense")

try:
    all_data = pd.read_csv("expenses.csv", header=None, names=["Added By", "Date", "Item", "Category", "Amount"])
    if len(all_data) == 0:
        st.write("No expenses to delete.")
    else:
        options = []
        for i in range(len(all_data)):
            row = all_data.iloc[i]
            label = str(row["Date"]) + " - " + str(row["Item"]) + " - " + str(row["Category"]) + " - " + str(row["Amount"]) + " (added by " + str(row["Added By"]) + ")"
            options.append(label)

        choice = st.selectbox("Pick an expense to delete", options)

        if st.button("Delete this expense"):
            index_to_delete = options.index(choice)
            all_data = all_data.drop(all_data.index[index_to_delete])
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
        if len(parts) == 5:
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
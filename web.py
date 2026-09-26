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
            if len(parts) == 3:
                users[parts[0]] = {"password": parts[1], "house": parts[2]}
    return users

def house_exists(house_code, users):
    for u in users:
        if users[u]["house"] == house_code:
            return True
    return False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "house_code" not in st.session_state:
    st.session_state.house_code = ""

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
                st.session_state.house_code = users[login_username]["house"]
                st.rerun()
            else:
                st.error("Incorrect username or password.")

    with tab2:
        new_username = st.text_input("Choose a username", key="new_username")
        new_password = st.text_input("Choose a password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
        house_choice = st.radio("House", ["Create a new house", "Join an existing house"])
        house_input = st.text_input("House code (make one up, e.g. CHENNAI2026, or enter the one your housemates gave you)")

        if st.button("Sign up"):
            users = load_users()
            if not new_username or not new_password or not house_input:
                st.warning("Please fill in all fields.")
            elif new_username in users:
                st.error("That username is already taken.")
            elif new_password != confirm_password:
                st.error("Passwords don't match.")
            elif house_choice == "Create a new house" and house_exists(house_input, users):
                st.error("That house code is already taken. Choose a different one, or select 'Join an existing house'.")
            elif house_choice == "Join an existing house" and not house_exists(house_input, users):
                st.error("No house found with that code. Check the code, or create a new house.")
            else:
                with open("users.csv", "a") as file:
                    file.write(new_username + "," + hash_password(new_password) + "," + house_input + "\n")
                st.session_state.logged_in = True
                st.session_state.username = new_username
                st.session_state.house_code = house_input
                st.success("Account created!")
                time.sleep(1)
                st.rerun()

    st.stop()

st.write("Logged in as: **" + st.session_state.username + "** (House: " + st.session_state.house_code + ")")
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.house_code = ""
    st.rerun()

username = st.session_state.username
house_code = st.session_state.house_code

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
            file.write(house_code + "," + username + "," + str(today) + "," + item + "," + category + "," + str(amount) + "\n")
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
        if len(parts) == 6 and parts[0] == house_code:
            day = parts[2]
            row_category = parts[4]
            amount_value = float(parts[5])
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
    all_data = pd.read_csv("expenses.csv", header=None, names=["House", "Added By", "Date", "Item", "Category", "Amount"])
    data = all_data[all_data["House"] == house_code].drop(columns=["House"])
    data = data.sort_values("Date", ascending=False)
    data.insert(0, "S.No", range(1, len(data) + 1))
    st.dataframe(data, width="stretch", hide_index=True)
except pd.errors.EmptyDataError:
    st.write("No expenses yet.")

st.divider()
st.subheader("Delete an Expense")

try:
    all_data = pd.read_csv("expenses.csv", header=None, names=["House", "Added By", "Date", "Item", "Category", "Amount"])
    delete_data = all_data[all_data["House"] == house_code].reset_index(drop=True)
    if len(delete_data) == 0:
        st.write("No expenses to delete.")
    else:
        options = []
        for i in range(len(delete_data)):
            row = delete_data.iloc[i]
            label = str(row["Date"]) + " - " + str(row["Item"]) + " - " + str(row["Category"]) + " - " + str(row["Amount"]) + " (added by " + str(row["Added By"]) + ")"
            options.append(label)

        choice = st.selectbox("Pick an expense to delete", options)

        if st.button("Delete this expense"):
            index_to_delete = options.index(choice)
            row_to_remove = delete_data.iloc[index_to_delete]
            match = (
                (all_data["House"] == row_to_remove["House"]) &
                (all_data["Added By"] == row_to_remove["Added By"]) &
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
        if len(parts) == 6 and parts[0] == house_code:
            month = parts[2][:7]
            amount_value = float(parts[5])
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


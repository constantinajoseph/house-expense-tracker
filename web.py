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

if not os.path.exists("houses.csv"):
    with open("houses.csv", "w") as file:
        pass

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_houses():
    houses = {}
    with open("houses.csv", "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 2:
                houses[parts[0]] = parts[1]
    return houses

def save_all_houses(houses):
    with open("houses.csv", "w") as file:
        for h in houses:
            file.write(h + "," + houses[h] + "\n")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "house_username" not in st.session_state:
    st.session_state.house_username = ""
if "email" not in st.session_state:
    st.session_state.email = ""

if not st.session_state.logged_in:
    st.subheader("Login or Create a House Account")
    tab1, tab2 = st.tabs(["Login", "Create House"])

    with tab1:
        st.write("Log in with your house's shared username and password, and your own email.")
        login_username = st.text_input("House username", key="login_username")
        login_password = st.text_input("House password", type="password", key="login_password")
        login_email = st.text_input("Your email", key="login_email")
        if st.button("Log in"):
            houses = load_houses()
            if not login_email:
                st.warning("Please enter your email.")
            elif login_username in houses and houses[login_username] == hash_password(login_password):
                st.session_state.logged_in = True
                st.session_state.house_username = login_username
                st.session_state.email = login_email
                st.rerun()
            else:
                st.error("Incorrect house username or password.")

        with st.expander("Forgot password?"):
            reset_username = st.text_input("House username", key="reset_username")
            reset_new_password = st.text_input("New password", type="password", key="reset_new_password")
            reset_confirm_password = st.text_input("Confirm new password", type="password", key="reset_confirm_password")

            if st.button("Reset Password"):
                houses = load_houses()
                if not reset_username or not reset_new_password:
                    st.warning("Please fill in all fields.")
                elif reset_username not in houses:
                    st.error("No house found with that username.")
                elif reset_new_password != reset_confirm_password:
                    st.error("Passwords don't match.")
                else:
                    houses[reset_username] = hash_password(reset_new_password)
                    save_all_houses(houses)
                    st.success("Password updated! You can log in now.")

    with tab2:
        st.write("Create a new house account. Share this username and password with your housemates.")
        new_username = st.text_input("Choose a house username", key="new_username")
        new_password = st.text_input("Choose a house password", type="password", key="new_password")
        confirm_password = st.text_input("Confirm password", type="password", key="confirm_password")
        new_email = st.text_input("Your email", key="new_email")

        if st.button("Create House"):
            houses = load_houses()
            if not new_username or not new_password or not new_email:
                st.warning("Please fill in all fields.")
            elif new_username in houses:
                st.error("That house username is already taken. Choose a different one.")
            elif new_password != confirm_password:
                st.error("Passwords don't match.")
            else:
                with open("houses.csv", "a") as file:
                    file.write(new_username + "," + hash_password(new_password) + "\n")
                st.session_state.logged_in = True
                st.session_state.house_username = new_username
                st.session_state.email = new_email
                st.success("House created!")
                time.sleep(1)
                st.rerun()

    st.stop()

st.write("Logged in as: **" + st.session_state.email + "** (House: " + st.session_state.house_username + ")")
if st.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.house_username = ""
    st.session_state.email = ""
    st.rerun()

house_username = st.session_state.house_username
email = st.session_state.email

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
            file.write(house_username + "," + email + "," + str(today) + "," + item + "," + category + "," + str(amount) + "\n")
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
        if len(parts) == 6 and parts[0] == house_username:
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
    data = all_data[all_data["House"] == house_username].drop(columns=["House"])
    data = data.sort_values("Date", ascending=False)
    data.insert(0, "S.No", range(1, len(data) + 1))
    st.dataframe(data, width="stretch", hide_index=True)
except pd.errors.EmptyDataError:
    st.write("No expenses yet.")

st.divider()
st.subheader("Delete an Expense")

try:
    all_data = pd.read_csv("expenses.csv", header=None, names=["House", "Added By", "Date", "Item", "Category", "Amount"])
    delete_data = all_data[all_data["House"] == house_username].reset_index(drop=True)
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
        if len(parts) == 6 and parts[0] == house_username:
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
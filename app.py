import time

import streamlit as st
import pymysql



@st.cache_resource
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="root",
        database="bank"
    )

connection = get_connection()
cursor = connection.cursor()

account_data={}

cursor.execute("SELECT * FROM accounts")
accounts= cursor.fetchall()

for account in accounts:
    account_data[account[0]] = account


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "show_create" not in st.session_state:
    st.session_state.show_create = False

if not st.session_state.logged_in:
    account_no = st.number_input("Account Number", min_value=1001)
    pin = st.text_input("PIN", type="password",key="login_pin")

    if st.button("Login"):

        if pin and pin.isdigit() and len(pin)==4:
            account=account_data.get(account_no)
            if account and account[3] ==int(pin):

                st.session_state.logged_in = True
                st.session_state.account_no = account_no
                st.session_state.name = account[1]
                st.success("Login successful")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid account number or PIN")

        else:
              st.error("Please enter your correct PIN ")



    if st.button("Create Account"):
        st.session_state.show_create = True

    if st.session_state.show_create:
            name = st.text_input("Enter Your name:")
            new_pin = st.text_input("PIN", type="password",key="Create_pin")
            balance = st.number_input("Balance", min_value=1000)
            if st.button("Save"):
                if new_pin and new_pin.isdigit() and len(new_pin)==4:
                    sql= "INSERT INTO accounts(name,pin,balance) VALUES(%s,%s,%s)"
                    cursor.execute(sql, (name, new_pin, balance))
                    connection.commit()
                    st.success("Account Created")
                    st.write("Your Account Number:", cursor.lastrowid)
                    st.session_state.show_create= False
                else:
                    st.error("Please enter your 4 digit pin")




else:

    st.success(f"Welcome {st.session_state.name}")
    choice=st.sidebar.selectbox(
        "Choose an option",
        [
            "Deposit",
            "Withdraw",
            "Check_balance",
            "Change_pin",
            "Delete_account"
        ]
    )


    if choice=="Deposit":


            amount = st.number_input("Enter your amount:", min_value=1)

            if st.button("Deposit"):

                sql = "UPDATE accounts SET balance = balance+ %s WHERE account_no= %s"
                cursor.execute(sql, (amount,st.session_state.account_no))
                connection.commit()
                st.success("Deposit successfully")

                cursor.execute("SELECT balance FROM accounts WHERE account_no=%s",(st.session_state.account_no,))
                current_balance = cursor.fetchone()
                if current_balance is None:
                    st.error("No Balance")
                else:
                    st.write("Current balance:", current_balance[0])



    elif choice=="Withdraw":

            amount = st.number_input("Enter your amount for withdraw:",min_value=1)

            if st.button("withdraw"):


                    cursor.execute("SELECT balance FROM accounts WHERE account_no=%s", (st.session_state.account_no,))
                    balance = cursor.fetchone()
                    if balance is None:
                        st.error("No Balance")
                    else:
                        if balance[0] >= amount:
                            sql = "UPDATE accounts SET balance =balance -%s WHERE account_no=%s"
                            cursor.execute(sql, (amount,st.session_state.account_no))
                            connection.commit()
                            st.success("Withdraw successful")
                            cursor.execute("SELECT balance FROM accounts WHERE account_no=%s", (st.session_state.account_no,))
                            current_balance = cursor.fetchone()
                            if current_balance is None:
                                st.error("No Balance")
                            else:
                                st.write("Current balance:", current_balance[0])

                        else:
                            st.error("Insufficient balance")

    elif choice=="Check_balance":


            if st.button("Check_balance"):

                    cursor.execute("SELECT balance from accounts WHERE account_no=%s", (st.session_state.account_no,))
                    balance = cursor.fetchone()
                    if balance is None:
                        st.error("No Balance")
                    else:
                        st.write("Current balance:", balance[0])



    elif choice=="Change_pin":


            new_pin = st.text_input("PIN:",type="password")
            if st.button("Change_pin"):
                if new_pin and new_pin.isdigit() and len(new_pin)==4:

                    sql = "UPDATE accounts SET pin=%s WHERE account_no=%s"
                    cursor.execute(sql, (new_pin, st.session_state.account_no))
                    connection.commit()
                    st.success("Pin successfully changed")
                    st.rerun()
                else:
                    st.error("Please enter your 4 digit pin")




    elif choice=="Delete_account":

            confirm = st.text_input("Are you sure want to delete the account?(yes/no)")


            if st.button("Delete_account"):


                if confirm and confirm.lower() == "yes":
                    sql = "DELETE FROM accounts WHERE account_no=%s"
                    cursor.execute(sql, (st.session_state.account_no,))
                    connection.commit()
                    time.sleep(1.5)
                    st.success("Account Deleted")
                    st.session_state.clear()
                    st.rerun()

                elif confirm and confirm.lower() == "no":
                    st.write("Process declined")
                else:
                 st.error("Enter 'yes' or 'no' only")


    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

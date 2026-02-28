import streamlit as st
from main import Bank

bank = Bank()

st.set_page_config(page_title="SecureBank", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

if "admin" not in st.session_state:
    st.session_state.admin = False

# ------------------ WELCOME PAGE ------------------

if not st.session_state.user and not st.session_state.admin:
    st.title("🏦 Welcome to SecureBank")
    st.write("Safe. Simple. Reliable Banking.")

    menu = st.selectbox("Select Option", ["Login", "Create Account", "Admin Login"])

    if menu == "Create Account":
        name = st.text_input("Full Name")
        acc_no = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")
        deposit = st.number_input("Initial Deposit", min_value=0.0)

        if st.button("Create Account"):
            success, msg = bank.create_account(name, acc_no, pin, deposit)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    elif menu == "Login":
        acc_no = st.text_input("Account Number")
        pin = st.text_input("PIN", type="password")

        if st.button("Login"):
            user = bank.login(acc_no, pin)
            if user:
                st.session_state.user = acc_no
                st.rerun()
            else:
                st.error("Invalid credentials")

    elif menu == "Admin Login":
        admin_pass = st.text_input("Admin Password", type="password")
        if st.button("Login as Admin"):
            if admin_pass == "admin123":
                st.session_state.admin = True
                st.rerun()
            else:
                st.error("Wrong admin password")

# ------------------ USER DASHBOARD ------------------

elif st.session_state.user:
    acc_no = st.session_state.user
    st.sidebar.title("User Menu")
    option = st.sidebar.radio("Choose", ["Deposit", "Withdraw", "Transfer",
                                         "Account Details", "Delete Account", "Logout"])

    if option == "Deposit":
        amount = st.number_input("Enter Amount", min_value=0.0)
        if st.button("Deposit"):
            bank.deposit(acc_no, amount)
            st.success("Amount deposited successfully")

    elif option == "Withdraw":
        amount = st.number_input("Enter Amount", min_value=0.0)
        if st.button("Withdraw"):
            if bank.withdraw(acc_no, amount):
                st.success("Amount withdrawn successfully")
            else:
                st.error("Insufficient balance")

    elif option == "Transfer":
        receiver = st.text_input("Receiver Account Number")
        amount = st.number_input("Enter Amount", min_value=0.0)
        if st.button("Send Money"):
            success, msg = bank.transfer(acc_no, receiver, amount)
            if success:
                st.success(msg)
            else:
                st.error(msg)

    elif option == "Account Details":
        user = bank.get_user_details(acc_no)
        st.subheader("Account Information")
        st.write(f"Name: {user[1]}")
        st.write(f"Account Number: {user[2]}")
        st.write(f"Balance: ₹{user[4]}")
        st.write(f"Created At: {user[5]}")

        st.subheader("Transaction History")
        transactions = bank.get_transactions(acc_no)
        for t in transactions:
            st.write(f"{t[2]} | {t[0]} | ₹{t[1]}")

    elif option == "Delete Account":
        confirm = st.checkbox("I understand this action is permanent")
        text_confirm = st.text_input("Type DELETE to confirm")

        if st.button("Delete My Account"):
            if confirm and text_confirm == "DELETE":
                bank.delete_account(acc_no)
                st.session_state.user = None
                st.success("Account deleted successfully")
                st.rerun()
            else:
                st.error("Confirmation failed")

    elif option == "Logout":
        st.session_state.user = None
        st.rerun()

# ------------------ ADMIN DASHBOARD ------------------

elif st.session_state.admin:
    st.title("Admin Dashboard")

    users = bank.get_all_users()
    st.subheader("All Users")
    for u in users:
        st.write(f"Account: {u[0]} | Name: {u[1]} | Balance: ₹{u[2]}")

    st.subheader("Total Bank Balance")
    st.write(f"₹{bank.total_bank_balance()}")

    if st.button("Logout Admin"):
        st.session_state.admin = False
        st.rerun()
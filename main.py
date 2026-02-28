import sqlite3
import hashlib
from datetime import datetime


class Bank:
    def __init__(self):
        self.conn = sqlite3.connect("bank.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            account_number TEXT UNIQUE NOT NULL,
            pin TEXT NOT NULL,
            balance REAL DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TEXT
        )
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_number TEXT,
            type TEXT,
            amount REAL,
            timestamp TEXT
        )
        """)
        self.conn.commit()

    def hash_pin(self, pin):
        return hashlib.sha256(pin.encode()).hexdigest()

    def create_account(self, name, acc_no, pin, initial_deposit):
        try:
            hashed_pin = self.hash_pin(pin)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute("""
            INSERT INTO users (name, account_number, pin, balance, created_at)
            VALUES (?, ?, ?, ?, ?)
            """, (name, acc_no, hashed_pin, initial_deposit, created_at))

            self.conn.commit()
            self.add_transaction(acc_no, "Initial Deposit", initial_deposit)
            return True, "Account created successfully"

        except sqlite3.IntegrityError:
            return False, "Account number already exists"

    def login(self, acc_no, pin):
        hashed_pin = self.hash_pin(pin)
        self.cursor.execute("""
        SELECT * FROM users WHERE account_number=? AND pin=?
        """, (acc_no, hashed_pin))
        return self.cursor.fetchone()

    def add_transaction(self, acc_no, t_type, amount):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
        INSERT INTO transactions (account_number, type, amount, timestamp)
        VALUES (?, ?, ?, ?)
        """, (acc_no, t_type, amount, timestamp))
        self.conn.commit()

    def deposit(self, acc_no, amount):
        user = self.get_user_details(acc_no)
        if user[5] == "Frozen":
            return False, "Account is frozen"

        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE account_number=?",
            (amount, acc_no))
        self.conn.commit()
        self.add_transaction(acc_no, "Deposit", amount)
        return True, "Deposit successful"

    def withdraw(self, acc_no, amount):
        user = self.get_user_details(acc_no)
        if user[5] == "Frozen":
            return False, "Account is frozen"

        balance = user[4]
        if balance < amount:
            return False, "Insufficient balance"

        self.cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE account_number=?",
            (amount, acc_no))
        self.conn.commit()
        self.add_transaction(acc_no, "Withdraw", amount)
        return True, "Withdraw successful"

    def transfer(self, sender, receiver, amount):
        sender_user = self.get_user_details(sender)
        receiver_user = self.get_user_details(receiver)

        if not sender_user or not receiver_user:
            return False, "Account not found"

        if sender_user[5] == "Frozen":
            return False, "Your account is frozen"

        if sender_user[4] < amount:
            return False, "Insufficient balance"

        self.cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE account_number=?",
            (amount, sender))
        self.cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE account_number=?",
            (amount, receiver))
        self.conn.commit()

        self.add_transaction(sender, "Transfer Sent", amount)
        self.add_transaction(receiver, "Transfer Received", amount)

        return True, "Transfer successful"

    def get_user_details(self, acc_no):
        self.cursor.execute(
            "SELECT * FROM users WHERE account_number=?", (acc_no,))
        return self.cursor.fetchone()

    def get_transactions(self, acc_no):
        self.cursor.execute("""
        SELECT type, amount, timestamp
        FROM transactions
        WHERE account_number=?
        """, (acc_no,))
        return self.cursor.fetchall()

    def delete_account(self, acc_no):
        self.cursor.execute("DELETE FROM users WHERE account_number=?", (acc_no,))
        self.cursor.execute("DELETE FROM transactions WHERE account_number=?", (acc_no,))
        self.conn.commit()

    def admin_delete_user(self, acc_no):
        self.delete_account(acc_no)

    def freeze_account(self, acc_no):
        self.cursor.execute(
            "UPDATE users SET status='Frozen' WHERE account_number=?",
            (acc_no,))
        self.conn.commit()

    def unfreeze_account(self, acc_no):
        self.cursor.execute(
            "UPDATE users SET status='Active' WHERE account_number=?",
            (acc_no,))
        self.conn.commit()

    def get_all_users(self):
        self.cursor.execute(
            "SELECT account_number, name, balance, status FROM users")
        return self.cursor.fetchall()

    def total_bank_balance(self):
        self.cursor.execute("SELECT SUM(balance) FROM users")
        result = self.cursor.fetchone()[0]
        return result if result else 0